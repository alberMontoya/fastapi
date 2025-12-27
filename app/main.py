from fastapi import Depends, FastAPI
from app import models
from .database import engine
from .routers import post, user, auth
from .config import settings

models.Base.metadata.create_all(bind=engine)

app = FastAPI()


@app.get('/')
def root():
	return {"hello": "world"}

app.include_router(post.router)
app.include_router(user.router)
app.include_router(auth.router)