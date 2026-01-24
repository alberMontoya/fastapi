import asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI
from app import models
from .database import engine
from .routers import post, user, auth, vote

#models.Base.metadata.create_all(bind=engine)
@asynccontextmanager
async def lifespan(app: FastAPI):
	async with engine.begin() as conn:
		# run_sync permite ejecutar funciones sincrónicas (como create_all)
		# dentro de una conexión asíncrona
		await conn.run_sync(models.Base.metadata.create_all)
		print(f"El driver activo es: {engine.dialect.driver}")
	yield
	print("Cerrando app")


app = FastAPI(lifespan=lifespan)


@app.get('/')
def root():
	return {"hello": "world"}

app.include_router(post.router)
app.include_router(user.router)
app.include_router(auth.router)
app.include_router(vote.router)