#!/usr/bin/env python3
"""Database seeding script from YAML configuration.

Usage:
    python scripts/seed_database.py seed_data.yaml
    python scripts/seed_database.py --help
"""

import asyncio
import logging
import sys
from pathlib import Path

import yaml
from dotenv import load_dotenv
from sqlalchemy import delete
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

# Load .env file from project root
project_root = Path(__file__).parent.parent.parent
load_dotenv(project_root / ".env")

# Add parent directory to path to import app modules
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.config import settings
from app.repositories.document_repository import DocumentRepository
from app.repositories.project import ProjectRepository
from app.repositories.project_doc import ProjectDocRepository
from app.schemas.project import ProjectCreate
from app.schemas.project_doc import ProjectDocCreate
from app.services.document_service import DocumentService
from app.services.github_service import GitHubService
from app.services.project_doc_service import ProjectDocService

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


async def clear_seeded_data(db: AsyncSession, project_name: str, project_doc_names: list[str]):
    """
    Clear only the specific project and project_docs that will be seeded.

    This is safer than clearing all data - it only removes data that matches
    the seed configuration.

    Args:
        db: Database session
        project_name: Name of the project to delete
        project_doc_names: Names of project_docs to delete under this project
    """
    from app.models.document import Document

    logger.info(f"🗑️  Clearing existing data for project '{project_name}'...")

    project_repo = ProjectRepository()
    project_doc_repo = ProjectDocRepository()

    # Find existing project by name
    existing_project = await project_repo.get_by_name(db, project_name)

    if existing_project:
        logger.info(f"   Found existing project: {existing_project.name} (ID: {existing_project.id})")

        # Delete specific project_docs by name
        for pd_name in project_doc_names:
            existing_pd = await project_doc_repo.get_by_name_and_project(
                db, existing_project.id, pd_name
            )
            if existing_pd:
                logger.info(f"   Deleting project_doc: {existing_pd.name}")
                # Delete associated documents (cascade should handle this, but being explicit)
                await db.execute(delete(Document).where(Document.project_doc_id == existing_pd.id))
                await project_doc_repo.delete(db, existing_pd.id)

        # Delete the project (this will cascade to remaining project_docs and documents)
        logger.info(f"   Deleting project: {existing_project.name}")
        await project_repo.delete(db, existing_project.id)

        logger.info("✓ Existing seed data cleared\n")
    else:
        logger.info("   No existing project found - nothing to clear\n")


async def seed_from_yaml(yaml_file: Path, skip_sync: bool = False, clear_first: bool = False):
    """
    Seed database from YAML configuration file.

    YAML format:
        project:
            name: Project Name
            description: Project description
            project_docs:
                - name: Doc Name
                  description: Doc description
                  github_url: https://github.com/user/repo.git
                  github_folder_path: docs

    Args:
        yaml_file: Path to YAML configuration file
        skip_sync: If True, skip automatic documentation sync
        clear_first: If True, clear existing project/project_docs matching seed config before seeding
    """
    # Load YAML
    logger.info(f"Loading configuration from {yaml_file}")
    with open(yaml_file, "r") as f:
        config = yaml.safe_load(f)

    if "project" not in config:
        raise ValueError("YAML must contain 'project' key")

    project_config = config["project"]

    # Create async engine and session
    engine = create_async_engine(settings.database_url, echo=False)
    async_session_factory = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with async_session_factory() as db:
        try:
            # Extract project_doc names for selective clearing
            project_docs_config = project_config.get("project_docs", [])
            if isinstance(project_docs_config, dict):
                project_docs_config = [project_docs_config]
            project_doc_names = [pd["name"] for pd in project_docs_config]

            # Clear existing data if requested (only the specific project and project_docs)
            if clear_first:
                await clear_seeded_data(db, project_config["name"], project_doc_names)

            # Get or Create Project
            project_repo = ProjectRepository()
            project_data = ProjectCreate(
                name=project_config["name"],
                description=project_config.get("description", ""),
            )

            # Check if project already exists
            project = await project_repo.get_by_name(db, project_data.name)
            if project:
                logger.info(f"Found existing project: {project.name} (ID: {project.id})")
            else:
                logger.info(f"Creating project: {project_data.name}")
                project = await project_repo.create(db, project_data)
                logger.info(f"✓ Created project {project.name} (ID: {project.id})")

            # Create ProjectDocs
            project_docs_config = project_config.get("project_docs", [])

            # Handle both single dict and list of dicts
            if isinstance(project_docs_config, dict):
                project_docs_config = [project_docs_config]

            project_doc_repo = ProjectDocRepository()

            # Initialize sync services
            github_service = GitHubService()
            document_repo = DocumentRepository(db)
            document_service = DocumentService(document_repo)
            sync_service = ProjectDocService(project_doc_repo, github_service, document_service)

            created_project_docs = []

            for doc_config in project_docs_config:
                doc_data = ProjectDocCreate(
                    name=doc_config["name"],
                    description=doc_config.get("description", ""),
                    github_url=doc_config["github_url"],
                    github_folder_path=doc_config.get("github_folder_path"),
                )

                # Check if project doc already exists
                project_doc = await project_doc_repo.get_by_name_and_project(
                    db, project.id, doc_data.name
                )
                if project_doc:
                    logger.info(f"  Found existing project doc: {project_doc.name} (ID: {project_doc.id})")
                else:
                    logger.info(f"  Creating project doc: {doc_data.name}")
                    project_doc = await project_doc_repo.create(db, project.id, doc_data)
                    logger.info(
                        f"  ✓ Created project doc {project_doc.name} (ID: {project_doc.id})"
                    )

                logger.info(f"    GitHub: {project_doc.github_url}")
                if project_doc.github_folder_path:
                    logger.info(f"    Folder: {project_doc.github_folder_path}")

                created_project_docs.append(project_doc)

            logger.info("\n✅ Database seeding completed successfully!")

            # Sync documentation for each ProjectDoc
            if skip_sync:
                logger.info("\n⏭️  Skipping documentation sync (--no-sync flag set)")
                logger.info("\nTo sync documentation manually, run:")
                for project_doc in created_project_docs:
                    logger.info(
                        f"  curl -X POST http://localhost:8000/api/project-docs/{project_doc.id}/sync"
                    )
            else:
                logger.info("\n📥 Starting documentation sync...")

                for project_doc in created_project_docs:
                    logger.info(f"\n  Syncing: {project_doc.name}")
                    logger.info(f"  Repository: {project_doc.github_url}")
                    if project_doc.github_folder_path:
                        logger.info(f"  Folder: {project_doc.github_folder_path}")

                    try:
                        sync_result = await sync_service.sync_project_doc(db, project_doc.id)

                        if sync_result.success:
                            logger.info(
                                f"  ✓ Sync completed: {sync_result.files_synced} files synced "
                                f"in {sync_result.duration_seconds:.2f}s"
                            )
                            if sync_result.files_failed > 0:
                                logger.warning(
                                    f"  ⚠ {sync_result.files_failed} files failed to sync"
                                )
                                for error in sync_result.errors[:3]:  # Show first 3 errors
                                    logger.warning(f"    - {error}")
                        else:
                            logger.error("  ✗ Sync failed!")
                            for error in sync_result.errors:
                                logger.error(f"    - {error}")

                    except Exception as e:
                        logger.error(f"  ✗ Sync error: {e}", exc_info=True)

                logger.info("\n✅ All operations completed!")

        except Exception as e:
            logger.error(f"❌ Error during seeding: {e}", exc_info=True)
            raise
        finally:
            await engine.dispose()


def main():
    """Main entry point."""
    if "--help" in sys.argv or "-h" in sys.argv:
        print("Usage: python scripts/seed_database.py [yaml_file] [--no-sync] [--clear]")
        print("\nArguments:")
        print("  yaml_file    Path to YAML seed file (default: scripts/seed_data.yaml)")
        print("\nOptions:")
        print("  --no-sync    Skip automatic documentation sync after seeding")
        print("  --clear      Clear existing project/project_docs matching the seed file before seeding")
        print("\nExample YAML format:")
        print(
            """
project:
    name: BMADFlow
    description: AI-Powered Documentation Chatbot
    project_docs:
        - name: Project Documentation
          description: BMAD Method generated Documentation
          github_url: https://github.com/twattier/bmadflow.git
          github_folder_path: docs
        """
        )
        sys.exit(0)

    # Determine YAML file - default to seed_data.yaml in scripts directory if not provided
    yaml_file_arg = None
    for arg in sys.argv[1:]:
        if not arg.startswith("--"):
            yaml_file_arg = arg
            break

    if yaml_file_arg:
        yaml_file = Path(yaml_file_arg)
    else:
        # Default to seed_data.yaml in the same directory as this script
        script_dir = Path(__file__).parent
        yaml_file = script_dir / "seed_data.yaml"
    skip_sync = "--no-sync" in sys.argv
    clear_first = "--clear" in sys.argv

    if not yaml_file.exists():
        logger.error(f"YAML file not found: {yaml_file}")
        sys.exit(1)

    asyncio.run(seed_from_yaml(yaml_file, skip_sync, clear_first))


if __name__ == "__main__":
    main()
