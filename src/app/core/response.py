from pydantic import BaseModel


class BaseError(BaseModel):
    detail: str


_STATUS_CODE_TO_DESCRIPTION = {
    403: 'Forbidden',
    404: 'Not Found',
}


def generate_openapi_error_responses(status_codes: set[int]):
    return {
        code: {'model': BaseError, 'description': descr}
        for code, descr in _STATUS_CODE_TO_DESCRIPTION.items()
        if code in status_codes
    }
