import uuid

from pydantic import Field
from sqlalchemy import Column, ForeignKey, Table, types
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.models import (
    AuditMixin,
    BaseSchema,
    BaseSQLModel,
    OwnerMixin,
    PrimaryUUIDMixin,
)
from app.slices.tag.models import Tag, TagPublic

from .constants import (
    NOTE_CONTENT_MAX_LENGTH,
    NOTE_NAME_MAX_LENGTH,
    NOTE_NAME_MIN_LENGTH,
)

note_tag_m2m = Table(
    'note_tag_m2m',
    BaseSQLModel.metadata,
    Column('note_id', ForeignKey('note.id')),
    Column('tag_id', ForeignKey('tag.id')),
)


class Note(PrimaryUUIDMixin, AuditMixin, OwnerMixin, BaseSQLModel):
    name: Mapped[str] = mapped_column(types.String(NOTE_NAME_MAX_LENGTH), nullable=False)
    content: Mapped[str] = mapped_column(types.String(NOTE_CONTENT_MAX_LENGTH), nullable=False)
    tags: Mapped[list[Tag]] = relationship(secondary=note_tag_m2m, lazy='joined', default_factory=list)


class NoteCreate(BaseSchema):
    name: str = Field(min_length=NOTE_NAME_MIN_LENGTH, max_length=NOTE_NAME_MAX_LENGTH)
    content: str = Field(max_length=NOTE_CONTENT_MAX_LENGTH)
    tags: list[str] = Field(default_factory=list)


class NoteUpdate(BaseSchema):
    name: str | None = Field(default=None)
    content: str | None = Field(default=None)
    tags: list[str] | None = Field(default=None)


class NotePublic(BaseSchema):
    id: uuid.UUID
    name: str
    content: str
    tags: list[TagPublic]
