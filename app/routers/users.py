from fastapi import Depends, FastAPI, Response, status, HTTPException, APIRouter
from typing import Optional, List
from .. import models, schemas, utils
from .. database import *
from sqlalchemy.orm import Session

router = APIRouter(
    prefix="/users",
    tags=["Users"])

@router.post("/", status_code=status.HTTP_201_CREATED, response_model=schemas.UserResponse)
def create_user(new_user: schemas.UserCreate, db: Session = Depends(get_db)):
    #hsh the password - user.password
    user_dict = new_user.model_dump()          # convert pydantic -> dict
    user_dict["password"] = utils.hash_password(user_dict["password"])  # replace password safely

    new_user_model = models.User(**user_dict)
    db.add(new_user_model)
    db.commit()
    db.refresh(new_user_model)
    return new_user_model

@router.get("/{id}", response_model=schemas.UserResponse)
def get_user(id: int, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.id == id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"user with id: {id} was not found")
    return user