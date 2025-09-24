import re
import uuid
from typing import Annotated

import jwt
from fastapi import Depends, HTTPException, Request
from passlib.context import CryptContext

from app.core.config import settings
from app.core.constants import JWT_ALGORITHM

auth_header_regex = re.compile('bearer (.*)', flags=re.IGNORECASE)
pwd_context = CryptContext(schemes=['bcrypt'])


def parse_token(token: str):
    try:
        claims = jwt.decode(token, settings.JWT_SECRET, algorithms=[JWT_ALGORITHM])
        return True, claims['sub']
    except jwt.PyJWTError:
        return False, None


async def get_current_user_id(request: Request) -> uuid.UUID:
    token = None

    authorization = request.headers.get('Authorization')
    if authorization:
        match = auth_header_regex.match(authorization)
        if match:
            token = match.groups()[0]

    if not token:
        raise HTTPException(
            status_code=401,
            detail='Not authenticated.',
            headers={'WWW-Authenticate': 'Bearer'},
        )

    ok, sub = parse_token(token)
    if ok:
        return uuid.UUID(sub)
    else:
        raise HTTPException(status_code=403, detail='Invalid token.')


CurrentUserIDDep = Annotated[uuid.UUID, Depends(get_current_user_id)]
