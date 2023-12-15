from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing_extensions import Annotated

from adapters.database import get_db
from repositories.post import get_posts, get_post_by_id, delete_post_by_id, update_post_by_id, create_post
from routes.user import validate_active_user
from schemas.post import Post, PostCreate, PostUpdate
from schemas.user import User

router = APIRouter()


@router.post("/create-post/", response_model=Post)
def create_user_post(
        current_user: Annotated[User, Depends(validate_active_user)],
        post: PostCreate,
        db: Session = Depends(get_db),
):
    return create_post(db=db, post=post, user_id=current_user.id)


@router.get("/list-posts/", response_model=list[Post])
def read_posts(db: Session = Depends(get_db)):
    posts = get_posts(db)
    return posts


@router.get("/get-post/{post_id}", response_model=Post)
def get_post(
        post_id: int,
        db: Session = Depends(get_db),
):
    db_post = get_post_by_id(db, post_id=post_id)
    if not db_post:
        raise HTTPException(status_code=404, detail="Post not found")
    return db_post


@router.delete("/delete-post/{post_id}", response_model=Post)
def delete_post(
        current_user: Annotated[User, Depends(validate_active_user)],
        post_id: int,
        db: Session = Depends(get_db),
):
    db_post = get_post_by_id(db, post_id=post_id)
    if not db_post:
        raise HTTPException(status_code=404, detail="Post not found")
    if current_user.id != db_post.author_id:
        raise HTTPException(status_code=403, detail="You do not have permission to delete this post")

    post = delete_post_by_id(db, post_id=post_id)
    return post


@router.patch("/update-post/{post_id}", response_model=Post)
def patch_post(
        current_user: Annotated[User, Depends(validate_active_user)],
        post_id: int,
        post: PostUpdate,
        db: Session = Depends(get_db),
):
    db_post = get_post_by_id(db, post_id=post_id)
    if not db_post:
        raise HTTPException(status_code=404, detail="Post not found")
    if current_user.id != db_post.author_id:
        raise HTTPException(status_code=403, detail="You do not have permission to update this post")

    post = update_post_by_id(db, post_id=post_id, post=post)
    return post
