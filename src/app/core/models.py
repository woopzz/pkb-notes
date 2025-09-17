import datetime as dt
import re
import uuid

from pydantic import BaseModel, ConfigDict
from sqlalchemy import types
from sqlalchemy.orm import DeclarativeBase, Mapped, MappedAsDataclass, declared_attr, mapped_column

from app.core.db import metadata


class BaseSQLModel(MappedAsDataclass, DeclarativeBase):
    metadata = metadata

    @declared_attr.directive
    def __tablename__(cls):
        names = re.split('(?=[A-Z])', cls.__name__)
        return '_'.join([x.lower() for x in names if x])


class BaseSchema(BaseModel):
    model_config = ConfigDict(
        from_attributes=True,
        str_strip_whitespace=True,
        validate_assignment=True,
    )


class PrimaryUUIDMixin(MappedAsDataclass):
    id: Mapped[uuid.UUID] = mapped_column(
        types.Uuid,
        primary_key=True,
        default_factory=uuid.uuid4,
        kw_only=True,
    )


class AuditMixin(MappedAsDataclass):
    created_at: Mapped[dt.datetime] = mapped_column(
        types.DateTime(timezone=True),
        default_factory=lambda: dt.datetime.now(dt.timezone.utc),
        nullable=False,
        kw_only=True,
    )
    updated_at: Mapped[dt.datetime] = mapped_column(
        types.DateTime(timezone=True),
        default_factory=lambda: dt.datetime.now(dt.timezone.utc),
        onupdate=lambda: dt.datetime.now(dt.timezone.utc),
        nullable=False,
        kw_only=True,
    )


class OwnerMixin(MappedAsDataclass):
    owner_id: Mapped[uuid.UUID] = mapped_column(types.Uuid, nullable=False)
