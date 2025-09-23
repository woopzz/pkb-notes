import uuid

from fastapi import APIRouter, HTTPException

from app.core.db import SessionDep
from app.core.response import generate_openapi_error_responses
from app.core.security import CurrentUserIDDep
from app.slices.tag.service import get_or_create_tags

from .models import Note, NoteCreate, NotePublic, NoteUpdate

router = APIRouter()


@router.get('/{id}', response_model=NotePublic, responses=generate_openapi_error_responses({403, 404}))
async def read_note(id: uuid.UUID, session: SessionDep, current_user_id: CurrentUserIDDep):
    note = await get_or_40x(session, current_user_id, id)
    return NotePublic.model_validate(note)


@router.post('/', response_model=NotePublic)
async def create_note(*, session: SessionDep, current_user_id: CurrentUserIDDep, note_in: NoteCreate):
    tags = await get_or_create_tags(session, current_user_id, note_in.tags)
    note = Note(
        name=note_in.name,
        content=note_in.content,
        tags=tags,
        owner_id=current_user_id,
    )
    session.add(note)
    await session.commit()
    return NotePublic.model_validate(note)


@router.patch('/{id}', status_code=204, responses=generate_openapi_error_responses({403, 404}))
async def update_note(
    *,
    session: SessionDep,
    current_user_id: CurrentUserIDDep,
    id: uuid.UUID,
    note_in: NoteUpdate,
):
    note = await get_or_40x(session, current_user_id, id)

    update_data = note_in.model_dump(exclude_unset=True)
    if not update_data:
        return

    for column, value in update_data.items():
        if column == 'tags':
            note.tags = await get_or_create_tags(session, note.owner_id, value)
        else:
            setattr(note, column, value)

    await session.commit()


@router.delete('/{id}', status_code=204, responses=generate_openapi_error_responses({403, 404}))
async def delete_note(*, session: SessionDep, current_user_id: CurrentUserIDDep, id: uuid.UUID):
    note = await get_or_40x(session, current_user_id, id)
    await session.delete(note)
    await session.commit()


async def get_or_40x(session: SessionDep, current_user_id: CurrentUserIDDep, id: uuid.UUID):
    note = await session.get(Note, id)
    if not note:
        raise HTTPException(status_code=404, detail=f'Note {id} was not found.')

    if note.owner_id != current_user_id:
        raise HTTPException(status_code=403, detail='You have access only to your notes. This one is not yours.')

    return note
