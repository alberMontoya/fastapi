import jwt
from app import schemas
from app.config import settings 
import pytest

#pytest -v -s -W ignore::DeprecationWarning
def test_root(client):
	response = client.get('/')
	assert response.status_code == 200
	assert response.json() == {'hello': 'world'}

def test_create_user(client):
	response = client.post('/user', json={
		'email': 'test@gmail.com',
		'password': 'testPassword123'
	})
	print(response)
	new_user = schemas.UserOut(**response.json())
	assert new_user.email == 'test@gmail.com'
	assert response.status_code == 201

def test_login(client, test_user):
	response = client.post('/login', data={
		'username': test_user['email'],
		'password': test_user['password']
	})
	log_response = schemas.Token(**response.json())
	payload = jwt.decode(log_response.access_token, settings.secret_key, algorithms=[settings.algorithm])
	id: str = payload.get('user_id')
	assert response.status_code == 200
	assert id == test_user['id']
	assert log_response.token_type == 'bearer'

@pytest.mark.parametrize('email, password, status_code',[
	('pepe@gmail.com', 'testPassword123', 403),
	('test@gmail.com', 'incorrect_password', 403),
	(None, 'testPassword123', 403),
	('test@gmail.com', None, 403),
	('pepe@gmail.com', 'incorrect_password', 403)
])
def test_incorrect_login(client, test_user, email, password, status_code):
	response = client.post('/login', data={
		'username': email,
		'password': password
	})

	assert response.status_code == status_code