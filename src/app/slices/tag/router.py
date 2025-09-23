import uuid

from fastapi import APIRouter, HTTPException

from app.core.db import SessionDep
from app.core.response import generate_openapi_error_responses
from app.core.security import CurrentUserIDDep

from .models import Tag, TagCreate, TagPublic, TagUpdate

router = APIRouter()


@router.get(
    '/{id}',
    response_model=TagPublic,
    responses=generate_openapi_error_responses({403, 404}),
)
async def read_tag(id: uuid.UUID, session: SessionDep, current_user_id: CurrentUserIDDep):
    tag = await get_or_40x(session, current_user_id, id)
    return TagPublic.model_validate(tag)


@router.post('/', response_model=TagPublic)
async def create_tag(*, session: SessionDep, current_user_id: CurrentUserIDDep, tag_in: TagCreate):
    tag = Tag(name=tag_in.name, owner_id=current_user_id)
    session.add(tag)
    await session.commit()
    return TagPublic.model_validate(tag)


@router.patch(
    '/{id}',
    status_code=204,
    responses=generate_openapi_error_responses({403, 404}),
)
async def update_tag(
    *,
    session: SessionDep,
    current_user_id: CurrentUserIDDep,
    id: uuid.UUID,
    tag_in: TagUpdate,
):
    tag = await get_or_40x(session, current_user_id, id)

    update_data = tag_in.model_dump(exclude_unset=True)
    if not update_data:
        return

    for column, value in update_data.items():
        setattr(tag, column, value)

    await session.commit()


@router.delete(
    '/{id}',
    status_code=204,
    responses=generate_openapi_error_responses({403, 404}),
)
async def delete_tag(*, session: SessionDep, current_user_id: CurrentUserIDDep, id: uuid.UUID):
    tag = await get_or_40x(session, current_user_id, id)
    await session.delete(tag)
    await session.commit()


async def get_or_40x(session: SessionDep, current_user_id: CurrentUserIDDep, id: uuid.UUID):
    tag = await session.get(Tag, id)
    if not tag:
        raise HTTPException(status_code=404, detail=f'Tag {id} was not found.')

    if tag.owner_id != current_user_id:
        raise HTTPException(
            status_code=403,
            detail='You have access only to your tags. This one is not yours.',
        )

    return tag
