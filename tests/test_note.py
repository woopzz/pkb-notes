import uuid
from collections.abc import Callable

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.slices.note.models import Note, NotePublic
from app.slices.tag.models import Tag, TagPublic

URL_NOTES = f'{settings.API_V1_STR}/notes/'


@pytest.mark.asyncio
@pytest.mark.parametrize(
    'name,content,tag_names',
    (
        ('name', 'content', ['t1', 't2']),
        ('only name', '', []),
    ),
)
async def test_create_note(
    client: AsyncClient,
    current_user_id: uuid.UUID,
    create_tag: Callable,
    name: str,
    content: str,
    tag_names: list[str],
):
    tags = []
    for name in tag_names:
        tag = await create_tag(name=name, owner_id=current_user_id)
        tags.append(TagPublic.model_validate(tag).model_dump(mode='json'))

    create_values = {
        'name': name,
        'content': content,
        'tags': tag_names,
        'owner_id': str(current_user_id),
    }
    response = await client.post(URL_NOTES, json=create_values)
    assert response.status_code == 200

    data = response.json()
    assert len(data) == 4
    assert uuid.UUID(data['id'])
    assert data['name'] == name
    assert data['content'] == content
    assert sorted(data['tags'], key=lambda x: x['id']) == sorted(tags, key=lambda x: x['id'])


@pytest.mark.asyncio
async def test_create_note_with_new_tag(session: AsyncSession, client: AsyncClient, current_user_id: uuid.UUID):
    """Should create a note and a tag, then bind the note with the tag."""
    tag_name = 'new tag'

    create_values = {
        'name': 'name',
        'content': '',
        'tags': [tag_name],
        'owner_id': str(current_user_id),
    }
    response = await client.post(URL_NOTES, json=create_values)
    assert response.status_code == 200

    data = response.json()
    assert len(data['tags']) == 1

    tag_id = uuid.UUID(data['tags'][0]['id'])
    tag = await session.get(Tag, tag_id)
    assert tag
    assert tag.name == tag_name
    assert tag.owner_id == current_user_id


@pytest.mark.asyncio
async def test_create_note_with_new_tag_for_note_owner(
    client: AsyncClient,
    current_user_id: uuid.UUID,
    create_tag: Callable,
):
    """Should create new tag if existing tags with the name have other owners."""
    tag_name = 'my tag'

    another_owner_id = uuid.uuid4()
    another_tag_with_same_name = await create_tag(name=tag_name, owner_id=another_owner_id)

    create_values = {
        'name': 'name',
        'content': '',
        'tags': [tag_name],
        'owner_id': str(current_user_id),
    }
    response = await client.post(URL_NOTES, json=create_values)
    assert response.status_code == 200

    data = response.json()
    assert len(data['tags']) == 1

    tag_info = data['tags'][0]
    assert tag_info['name'] == another_tag_with_same_name.name
    assert tag_info['id'] != str(another_tag_with_same_name.id)


@pytest.mark.asyncio
@pytest.mark.parametrize(
    'update_values',
    (
        {},
        {'name': 'new name', 'content': 'new content', 'tags': ['new tag']},
        {'name': 'another name'},
        {'content': 'another content'},
        {'tags': ['qwe', 'rty']},
    ),
)
async def test_update_note(
    session: AsyncSession,
    client: AsyncClient,
    create_tag: Callable,
    create_note: Callable,
    update_values: dict,
):
    note = await create_note()

    tags = []
    for name in update_values.get('tags', []):
        tag = await create_tag(name=name)
        tags.append(TagPublic.model_validate(tag).model_dump(mode='json'))

    response = await client.patch(URL_NOTES + str(note.id), json=update_values)
    assert response.status_code == 204

    note = await session.get(Note, note.id)
    for column, value in update_values.items():
        if column == 'tags':
            assert set(x.name for x in note.tags) == set(value)
        else:
            assert getattr(note, column) == value


@pytest.mark.asyncio
async def test_update_note_with_new_tag(
    session: AsyncSession,
    client: AsyncClient,
    create_note: Callable,
):
    """Should create a tag, then bind the tag with the note."""
    note = await create_note()
    tag_name = 'create a new tag for me pls'

    response = await client.patch(URL_NOTES + str(note.id), json={'tags': [tag_name]})
    assert response.status_code == 204

    note = await session.get(Note, note.id)
    assert len(note.tags) == 1
    assert note.tags[0].name == tag_name
    assert note.tags[0].owner_id == note.owner_id


@pytest.mark.asyncio
async def test_read_note(
    client: AsyncClient,
    create_tag: Callable,
    create_note: Callable,
):
    tag = await create_tag()
    note = await create_note(content='some content', tags=[tag])

    response = await client.get(URL_NOTES + str(note.id))
    assert response.status_code == 200
    assert NotePublic.model_validate(response.json()) == NotePublic.model_validate(note)


@pytest.mark.asyncio
async def test_read_missing_note(client: AsyncClient):
    """Should return 404 if the note does not exist."""
    note_id = uuid.uuid4()
    response = await client.get(URL_NOTES + str(note_id))
    assert response.status_code == 404
    assert response.json() == {'detail': f'Note {note_id} was not found.'}


@pytest.mark.asyncio
async def test_delete_note(
    session: AsyncSession,
    client: AsyncClient,
    create_note: Callable,
):
    note = await create_note()
    assert note == await session.get(Note, note.id)

    response = await client.delete(URL_NOTES + str(note.id))
    assert response.status_code == 204

    assert None is await session.get(Note, note.id)


@pytest.mark.asyncio
async def test_delete_missing_note(client: AsyncClient):
    """Should return 404 if the note does not exist."""
    note_id = uuid.uuid4()
    response = await client.delete(URL_NOTES + str(note_id))
    assert response.status_code == 404
    assert response.json() == {'detail': f'Note {note_id} was not found.'}
