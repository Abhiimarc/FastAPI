from pydantic import BaseModel, ConfigDict, EmailStr
from datetime import datetime
from typing import Optional




class UserCreate(BaseModel):
    email: EmailStr
    password: str

class UserResponse(BaseModel):
    id: int
    email: EmailStr
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class PostBase(BaseModel):
    content: str
    title: str
    published: bool = True

    
class PostResponse(PostBase):
    id: int
    created_at: datetime
    user_id: int
    owner: UserResponse
    model_config = ConfigDict(from_attributes=True)

class PostWithVotes(BaseModel):
    Post: PostResponse
    votes: int
    model_config = ConfigDict(from_attributes=True)
    

class PostCreate(PostBase):
    pass


class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    id: Optional[int] = None

class VoteCreate(BaseModel):
    post_id: int
    dir: int