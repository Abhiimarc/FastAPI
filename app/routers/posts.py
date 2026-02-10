from fastapi import Depends, FastAPI, Response, status, HTTPException, APIRouter
from fastapi.params import Body
from typing import Optional, List
from .. import models, schemas, utils, oauth2
from ..database import *
from sqlalchemy.orm import Session
from sqlalchemy import func

router = APIRouter(prefix="/posts", tags=["Posts"])


# @router.get("/", response_model=List[schemas.PostResponse])
@router.get("/", response_model=List[schemas.PostWithVotes])
def all_posts(
    db: Session = Depends(get_db),
    current_user=Depends(oauth2.get_current_user),
    limit: int = 10,
    skip: int = 0,
):
    # posts=db.query(models.Post).offset(skip).limit(limit).all()
    posts = (
        db.query(models.Post, func.count(models.Vote.post_id).label("votes"))
        .join(models.Vote, models.Vote.post_id == models.Post.id, isouter=True)
        .group_by(models.Post.id)
        .offset(skip)
        .limit(limit)
        .all()
    )
    return posts


@router.post(
    "/", status_code=status.HTTP_201_CREATED, response_model=schemas.PostResponse
)
def create_posts(
    new_post: schemas.PostCreate,
    db: Session = Depends(get_db),
    current_user=Depends(oauth2.get_current_user),
):
    new_post_model = models.Post(user_id=current_user.id, **new_post.model_dump())
    db.add(new_post_model)
    db.commit()
    db.refresh(new_post_model)
    return new_post_model


@router.get("/{post_id}", response_model=schemas.PostWithVotes)
def get_post(
    post_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(oauth2.get_current_user),
):
    # post = db.query(models.Post).filter(models.Post.id == post_id).first()
    post = (
        db.query(models.Post, func.count(models.Vote.post_id).label("votes"))
        .join(models.Vote, models.Vote.post_id == models.Post.id, isouter=True)
        .group_by(models.Post.id)
        .filter(models.Post.id == post_id)
        .first()
    )
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"post with id: {post_id} was not found",
        )
    return post


@router.delete("/{post_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_post(
    post_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(oauth2.get_current_user),
):
    post_query = db.query(models.Post).filter(models.Post.id == post_id)
    deleted_post = post_query.first()
    if deleted_post is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"post with id: {post_id} does not exist",
        )
    if deleted_post.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Not authorized to perform requested action",
        )
    post_query.delete(synchronize_session=False)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.put("/{post_id}")
def update_post(
    post_id: int,
    updated_post: schemas.PostCreate,
    db: Session = Depends(get_db),
    current_user=Depends(oauth2.get_current_user),
):
    post_query = db.query(models.Post).filter(models.Post.id == post_id)
    post = post_query.first()
    if post is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"post with id: {post_id} does not exist",
        )
    if post.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Not authorized to perform requested action",
        )
    post_query.update(updated_post.model_dump(), synchronize_session=False)
    db.commit()
    return post_query.first()
