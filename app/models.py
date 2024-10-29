from pydantic import BaseModel


class GenericException(BaseModel):
    detail: str
