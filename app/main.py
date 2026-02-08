from fastapi import FastAPI
from random import randrange
from . import models
from .database import *
from . routers import posts, users, auth, vote
from fastapi.middleware.cors import CORSMiddleware


# models.Base.metadata.create_all(bind=engine)

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
    allow_credentials=True,)

app.include_router(posts.router)
app.include_router(users.router)
app.include_router(auth.router)
app.include_router(vote.router)

@app.get("/")
def read_root():
    return {"Hello": "What's up!"}
