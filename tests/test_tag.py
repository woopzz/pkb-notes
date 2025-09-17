import uuid

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.slices.tag.models import Tag, TagPublic

from .utils import create_tag

URL_TAGS = f'{settings.API_V1_STR}/tags/'


@pytest.mark.asyncio
async def test_create_tag(client: AsyncClient):
    name = 'test'
    owner_id = uuid.uuid4()

    response = await client.post(URL_TAGS, json={'name': name, 'owner_id': str(owner_id)})
    assert response.status_code == 200

    data = response.json()
    assert len(data) == 3
    assert uuid.UUID(data['id'])
    assert data['name'] == name
    assert data['owner_id'] == str(owner_id)


@pytest.mark.asyncio
async def test_update_tag(session: AsyncSession, client: AsyncClient):
    tag = await create_tag(session)
    new_name = 'new name'

    response = await client.patch(URL_TAGS + str(tag.id), json={'name': new_name})
    assert response.status_code == 204

    tag = await session.get(Tag, tag.id)
    assert tag.name == new_name


@pytest.mark.asyncio
async def test_read_tag(session: AsyncSession, client: AsyncClient):
    tag = await create_tag(session)

    response = await client.get(URL_TAGS + str(tag.id))
    assert response.status_code == 200
    assert TagPublic.model_validate(response.json()) == TagPublic.model_validate(tag)


@pytest.mark.asyncio
async def test_read_missing_tag(client: AsyncClient):
    """Should return 404 if the tag does not exist."""
    tag_id = uuid.uuid4()
    response = await client.get(URL_TAGS + str(tag_id))
    assert response.status_code == 404
    assert response.json() == {'detail': f'Tag {tag_id} was not found.'}


@pytest.mark.asyncio
async def test_delete_tag(session: AsyncSession, client: AsyncClient):
    tag = await create_tag(session)
    assert tag == await session.get(Tag, tag.id)

    response = await client.delete(URL_TAGS + str(tag.id))
    assert response.status_code == 204

    assert None is await session.get(Tag, tag.id)


@pytest.mark.asyncio
async def test_delete_missing_tag(client: AsyncClient):
    """Should return 404 if the tag does not exist."""
    tag_id = uuid.uuid4()
    response = await client.delete(URL_TAGS + str(tag_id))
    assert response.status_code == 404
    assert response.json() == {'detail': f'Tag {tag_id} was not found.'}
