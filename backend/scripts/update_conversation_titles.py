"""One-time script to update existing 'New Conversation' titles with first message content."""

import asyncio
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, selectinload

from app.config import settings
from app.models.conversation import Conversation
from app.models.message import Message


async def update_conversation_titles():
    """Update all conversations with 'New Conversation' title to use first message content."""

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

        updated_count = 0
        for conv in conversations:
            if not conv.messages:
                print(f"  Skipping {conv.id} - no messages")
                continue

            # Get first user message
            first_message = None
            for msg in sorted(conv.messages, key=lambda m: m.created_at):
                if msg.role == "user":
                    first_message = msg
                    break

            if not first_message:
                print(f"  Skipping {conv.id} - no user messages")
                continue

            # Generate title from first message
            title = first_message.content[:50].strip()
            if len(first_message.content) > 50:
                title += "..."

            # Update conversation title
            await session.execute(
                update(Conversation)
                .where(Conversation.id == conv.id)
                .values(title=title)
            )
            updated_count += 1
            print(f"  Updated {conv.id}: '{title}'")

        await session.commit()
        print(f"\n✅ Updated {updated_count} conversations")

    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(update_conversation_titles())
