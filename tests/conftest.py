import pytest
import pytest_asyncio
import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.pool import NullPool
from httpx import ASGITransport, AsyncClient

from app import models
from app.database import get_db
from app.config import settings
from app.main import app

SQLALCHEMY_DATABASE_URL = f'postgresql+asyncpg://{settings.database_username}:{settings.database_password}@{settings.database_hostname}/{settings.database_name}_test'

# 1. Creamos el motor fuera de los fixtures para manejar su cierre globalmente
async_engine = create_async_engine(
	SQLALCHEMY_DATABASE_URL, 
	echo=True, 
	poolclass=NullPool
)

'''@pytest.fixture(scope="session")
def event_loop():
	"""Configuración del loop para evitar 'Event loop is closed' en Windows."""
	policy = asyncio.get_event_loop_policy()
	loop = policy.new_event_loop()
	yield loop
	# Antes de cerrar el loop, le damos un respiro para limpiar tareas pendientes
	loop.run_until_complete(asyncio.sleep(0))
	loop.close()
'''

@pytest_asyncio.fixture(scope="function") 
async def async_db_engine():
	"""Prepara las tablas antes de CADA test individual."""
	async with async_engine.begin() as conn:
		await conn.run_sync(models.Base.metadata.drop_all)
		await conn.run_sync(models.Base.metadata.create_all)
	yield async_engine
	await async_engine.dispose()

# 2. Asegúrate de que async_db limpie bien la conexión al terminar
@pytest_asyncio.fixture(scope="function")
async def async_db(async_db_engine):
	TestingSessionLocal = async_sessionmaker(
		bind=async_db_engine, 
		class_=AsyncSession, 
		expire_on_commit=False
	)

	async with TestingSessionLocal() as session:
		yield session
		# Forzamos limpieza para evitar que Windows deje conexiones colgadas
		await session.close()

@pytest_asyncio.fixture(scope="function")
async def async_client(async_db):
	"""Cliente HTTP asíncrono."""
	async def override_get_db():
		yield async_db

	app.dependency_overrides[get_db] = override_get_db
	
	async with AsyncClient(transport=ASGITransport(app=app), base_url="http://localhost") as ac:
		yield ac
	
	app.dependency_overrides.clear()

@pytest_asyncio.fixture(scope="function")
async def test_user(async_client):
	user = {
		"email": "test@gmail.com",
		"password": "testPassword123"
	}
	response = await async_client.post('/user', json=user)
	if response.status_code != 201:
		print(f"DEBUG: {response.json()}") # Esto te dirá el mensaje real (ej: "Email already exists")
	assert response.status_code == 201
	new_user = response.json()
	new_user['password'] = user["password"]
	return new_user
