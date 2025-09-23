import uuid

from pydantic import Field
from sqlalchemy import UniqueConstraint, types
from sqlalchemy.orm import Mapped, mapped_column

from app.core.models import AuditMixin, BaseSchema, BaseSQLModel, OwnerMixin, PrimaryUUIDMixin

from .constants import TAG_NAME_MAX_LENGTH, TAG_NAME_MIN_LENGTH


class Tag(PrimaryUUIDMixin, AuditMixin, OwnerMixin, BaseSQLModel):
    __table_args__ = (UniqueConstraint('name', 'owner_id', name='unique_name_owner'),)

    name: Mapped[str] = mapped_column(types.String(TAG_NAME_MAX_LENGTH), nullable=False)


class TagCreate(BaseSchema):
    name: str = Field(min_length=TAG_NAME_MIN_LENGTH, max_length=TAG_NAME_MAX_LENGTH)


class TagUpdate(BaseSchema):
    name: str | None = Field(default=None)


class TagPublic(BaseSchema):
    id: uuid.UUID
    name: str
