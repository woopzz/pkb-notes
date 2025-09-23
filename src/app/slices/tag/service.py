import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.slices.tag.models import Tag


async def get_or_create_tags(
    session: AsyncSession,
    owner_id: uuid.UUID,
    tag_names: list[str],
) -> list[Tag]:
    tags = []
    if not tag_names:
        return tags

    query = select(Tag).where(Tag.name.in_(tag_names)).where(Tag.owner_id == owner_id)
    result = await session.execute(query)
    tags.extend(result.scalars().all())

    if len(tag_names) > len(tags):
        new_tag_names = set(tag_names) - set(x.name for x in tags)
        new_tags = [Tag(name=x, owner_id=owner_id) for x in new_tag_names]
        session.add_all(new_tags)
        tags.extend(new_tags)

    return tags
