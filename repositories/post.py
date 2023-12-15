from sqlalchemy.orm import Session

from models.posts import Post
from schemas.post import PostCreate, PostUpdate


def get_posts(db: Session):
    return db.query(Post).all()


def get_post_by_id(db: Session, post_id: int):
    return db.query(Post).filter(Post.id == post_id).first()


def create_post(db: Session, post: PostCreate, user_id: int):
    db_post = Post(**post.model_dump(), author_id=user_id)
    db.add(db_post)
    db.commit()
    db.refresh(db_post)
    return db_post


def delete_post_by_id(db: Session, post_id: int):
    db_post = db.query(Post).filter(Post.id == post_id).first()

    if db_post:
        db.delete(db_post)
        db.commit()
        return db_post
    return None


def update_post_by_id(db: Session, post_id: int, post: PostUpdate):
    db_post = db.query(Post).filter(Post.id == post_id).first()

    if db_post:
        for field, value in post.model_dump().items():
            setattr(db_post, field, value)

        db.commit()
        db.refresh(db_post)
        return db_post
    return None
