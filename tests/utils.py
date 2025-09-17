import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from app.slices.note.models import Note
from app.slices.tag.models import Tag


async def create_note(session: AsyncSession, **values) -> Note:
    values.setdefault('name', 'test')
    values.setdefault('content', '')
    values.setdefault('owner_id', uuid.uuid4())
    note = Note(**values)

    session.add(note)
    await session.commit()
    return note


async def create_tag(session: AsyncSession, **values) -> Tag:
    values.setdefault('name', 'test')
    values.setdefault('owner_id', uuid.uuid4())
    tag = Tag(**values)

    session.add(tag)
    await session.commit()
    return tag
