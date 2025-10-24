import uuid

from pgvector.sqlalchemy import Vector
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
    NOTE_PAGE_LIMIT_MAX,
    NOTE_PAGE_SIZE,
    SENTENCE_TRANSFORMERS_EMBEDDING_SIZE,
)

note_tag_m2m = Table(
    'note_tag_m2m',
    BaseSQLModel.metadata,
    Column('note_id', ForeignKey('note.id', ondelete='CASCADE')),
    Column('tag_id', ForeignKey('tag.id', ondelete='CASCADE')),
)


class Note(PrimaryUUIDMixin, AuditMixin, OwnerMixin, BaseSQLModel):
    name: Mapped[str] = mapped_column(types.String(NOTE_NAME_MAX_LENGTH), nullable=False)
    content: Mapped[str] = mapped_column(types.String(NOTE_CONTENT_MAX_LENGTH), nullable=False)
    embedding: Mapped[list[float]] = mapped_column(
        Vector(SENTENCE_TRANSFORMERS_EMBEDDING_SIZE),
        nullable=False,
    )
    tags: Mapped[list[Tag]] = relationship(
        secondary=note_tag_m2m,
        lazy='joined',
        default_factory=list,
    )


class NotesRead(BaseSchema):
    q: str | None = Field(default=None)
    offset: int = Field(default=0, ge=0, le=NOTE_PAGE_LIMIT_MAX)
    limit: int = Field(default=NOTE_PAGE_SIZE, ge=0)


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
