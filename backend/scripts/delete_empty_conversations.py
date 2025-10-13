"""One-time script to delete empty conversations with 'New Conversation' title."""

import asyncio
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, selectinload

from app.config import settings
from app.models.conversation import Conversation


async def delete_empty_conversations():
    """Delete all conversations with 'New Conversation' title that have no messages."""

    # Create async engine
    engine = create_async_engine(settings.database_url, echo=True)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with async_session() as session:
        # Get all conversations with 'New Conversation' title
        result = await session.execute(
            select(Conversation)
            .where(Conversation.title == "New Conversation")
            .options(selectinload(Conversation.messages))
        )
        conversations = result.scalars().all()

        print(f"\nFound {len(conversations)} conversations with 'New Conversation' title")

        deleted_count = 0
        for conv in conversations:
            if len(conv.messages) == 0:
                # Delete empty conversation
                await session.execute(
                    delete(Conversation).where(Conversation.id == conv.id)
                )
                deleted_count += 1
                print(f"  Deleted empty conversation {conv.id}")
            else:
                print(f"  Skipped {conv.id} - has {len(conv.messages)} messages")

        await session.commit()
        print(f"\n✅ Deleted {deleted_count} empty conversations")

    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(delete_empty_conversations())
