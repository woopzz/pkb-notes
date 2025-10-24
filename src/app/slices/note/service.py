import uuid
from collections import defaultdict

from sentence_transformers import SentenceTransformer
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from .models import Note, Tag, note_tag_m2m


def get_embedding(st: SentenceTransformer, name: str, content: str):
    source = '. '.join(filter(None, (name, content)))
    return st.encode(source).tolist()


def create(session: AsyncSession, st: SentenceTransformer, **kwargs):
    if 'embedding' not in kwargs:
        kwargs['embedding'] = get_embedding(st, kwargs['name'], kwargs['content'])

    note = Note(**kwargs)
    session.add(note)
    return note


def update(st: SentenceTransformer, note: Note, **kwargs):
    for column, value in kwargs.items():
        setattr(note, column, value)

    if 'name' in kwargs or 'content' in kwargs:
        note.embedding = get_embedding(st, note.name, note.content)


async def search_notes(
    session: AsyncSession,
    owner_id: uuid.UUID,
    st: SentenceTransformer,
    query: str | None,
    offset: int,
    limit: int,
):
    note_query = (
        select(Note.id, Note.name, Note.content)
        .where(Note.owner_id == owner_id)
        .offset(offset)
        .limit(limit)
    )

    if query:
        query_embedding = st.encode([query])[0]
        score = 1 - Note.embedding.cosine_distance(query_embedding)
        note_query = (
            note_query.where(Note.embedding.is_not(None)).where(score > 0.1).order_by(score.desc())
        )

    note_query = note_query.order_by(Note.created_at.desc())

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
