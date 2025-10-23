import uuid
from collections import defaultdict

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from .models import Note, Tag, note_tag_m2m


async def search_notes(
    session: AsyncSession,
    owner_id: uuid.UUID,
    offset: int,
    limit: int,
):
    note_query = (
        select(Note.id, Note.name, Note.content)
        .where(Note.owner_id == owner_id)
        .order_by(Note.created_at.desc())
        .offset(offset)
        .limit(limit)
    )
    result = await session.execute(note_query)
    raw_notes = result.fetchall()

    note_id_to_tag = defaultdict(list)
    if raw_notes:
        note_ids = [x[0] for x in raw_notes]
        tag_query = (
            select(Tag.id, Tag.name, Note.id)
            .outerjoin(note_tag_m2m, note_tag_m2m.c.tag_id == Tag.id)
            .join(Note, Note.id == note_tag_m2m.c.note_id)
            .where(Tag.owner_id == owner_id)
            .where(Note.id.in_(note_ids))
        )
        result = await session.execute(tag_query)

        for tag_id, tag_name, note_id in result:
            note_id_to_tag[note_id].append({'id': tag_id, 'name': tag_name})

    return [
        {'id': id_, 'name': name, 'content': content, 'tags': note_id_to_tag[id_]}
        for id_, name, content in raw_notes
    ]
