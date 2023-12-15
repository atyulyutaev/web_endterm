from pydantic import BaseModel


class PostBase(BaseModel):
    title: str
    text: str | None = None


class PostCreate(PostBase):
    pass


class PostUpdate(PostBase):
    pass


class Post(PostBase):
    id: int
    author_id: int

    class Config:
        orm_mode = True
