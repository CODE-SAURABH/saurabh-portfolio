from pydantic import BaseModel


class DataResponse[T](BaseModel):
    data: T


class PaginationMeta(BaseModel):
    total: int
    offset: int
    limit: int


class CollectionResponse[T](BaseModel):
    data: list[T]
    meta: PaginationMeta


class MessageData(BaseModel):
    message: str
