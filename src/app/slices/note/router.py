import uuid
from typing import Annotated

from fastapi import APIRouter, HTTPException, Query, Request

from app.core.db import SessionDep
from app.core.response import generate_openapi_error_responses
from app.core.security import CurrentUserIDDep
from app.slices.tag.service import get_or_create_tags

from .models import Note, NoteCreate, NotePublic, NotesRead, NoteUpdate
from .service import create, search_notes, update

router = APIRouter()


@router.get(
    '/{id}',
    response_model=NotePublic,
    responses=generate_openapi_error_responses({403, 404}),
)
async def read_note(id: uuid.UUID, session: SessionDep, current_user_id: CurrentUserIDDep):
    note = await get_or_40x(session, current_user_id, id)
    return NotePublic.model_validate(note)


@router.get('/')
async def read_notes(
    *,
    request: Request,
    session: SessionDep,
    current_user_id: CurrentUserIDDep,
    params: Annotated[NotesRead, Query()],
) -> list[NotePublic]:
    st = request.state.st
    return await search_notes(session, current_user_id, st, params.q, params.offset, params.limit)


@router.post('/', response_model=NotePublic)
async def create_note(
    *,
    request: Request,
    session: SessionDep,
    current_user_id: CurrentUserIDDep,
    note_in: NoteCreate,
):
    st = request.state.st
    tags = await get_or_create_tags(session, current_user_id, note_in.tags)
    note = create(
        session,
        st,
        name=note_in.name,
        content=note_in.content,
        tags=tags,
        owner_id=current_user_id,
    )
    await session.commit()
    return NotePublic.model_validate(note)


@router.patch(
    '/{id}',
    status_code=204,
    responses=generate_openapi_error_responses({403, 404}),
)
async def update_note(
    *,
    request: Request,
    session: SessionDep,
    current_user_id: CurrentUserIDDep,
    id: uuid.UUID,
    note_in: NoteUpdate,
):
    note = await get_or_40x(session, current_user_id, id)
    update_data = note_in.model_dump(exclude_unset=True)

    if 'tags' in update_data:
        update_data['tags'] = await get_or_create_tags(session, note.owner_id, update_data['tags'])

    if update_data:
        st = request.state.st
        update(st, note, **update_data)
        await session.commit()


@router.delete(
    '/{id}',
    status_code=204,
    responses=generate_openapi_error_responses({403, 404}),
)
async def delete_note(*, session: SessionDep, current_user_id: CurrentUserIDDep, id: uuid.UUID):
    note = await get_or_40x(session, current_user_id, id)
    await session.delete(note)
    await session.commit()


async def get_or_40x(session: SessionDep, current_user_id: CurrentUserIDDep, id: uuid.UUID):
    note = await session.get(Note, id)
    if not note:
        raise HTTPException(status_code=404, detail=f'Note {id} was not found.')

    if note.owner_id != current_user_id:
        raise HTTPException(
            status_code=403,
            detail='You have access only to your notes. This one is not yours.',
        )

    return note
