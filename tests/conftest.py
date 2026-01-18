from app import models
import app
from fastapi.testclient import TestClient
from app.database import get_db
from app.config import settings
from app.main import app
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import pytest


SQLALCHEMY_DATABASE_URL =f'postgresql+psycopg://{settings.database_username}:{settings.database_password}@{settings.database_hostname}/{settings.database_name}_test'

engine = create_engine(SQLALCHEMY_DATABASE_URL)

#print(f"Estás usando Psycopg 3: {psycopg.__version__}")
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
#pytest -v -s -W ignore::DeprecationWarning

@pytest.fixture
def session():
	models.Base.metadata.drop_all(bind=engine)
	models.Base.metadata.create_all(bind=engine)
	db = TestingSessionLocal()
	try:
		yield db
	finally:
		db.close()

@pytest.fixture
def client(session):
	def override_get_db():
		try:
			yield session
		finally:
			session.close()
	app.dependency_overrides[get_db] = override_get_db
	yield TestClient(app)

@pytest.fixture
def test_user(client):
	user = {
		"email": "test@gmail.com",
		"password": "testPassword123"
	}
	response = client.post('/user', json=user)
	assert response.status_code == 201
	new_user = response.json()
	new_user['password'] = user["password"]
	return new_user