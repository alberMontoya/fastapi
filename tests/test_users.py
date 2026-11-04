import jwt
from app import schemas
from app.config import settings 
import pytest

#pytest -v -s -W ignore::DeprecationWarning
#pytestmark = pytest.mark.asyncio

async def test_root(async_client):
	response = await async_client.get('/')
	assert response.status_code == 200
	assert response.json() == {'hello': 'world'}

async def test_create_user(async_client):
	response = await async_client.post('/user', json={
		'email': 'test@gmail.com',
		'password': 'testPassword123'
	})
	print(response)
	assert response.status_code == 201
	new_user = schemas.UserOut(**response.json())
	assert new_user.email == 'test@gmail.com'
	
@pytest.mark.asyncio(loop_scope="function")
async def test_login(async_client, test_user):
	response = await async_client.post('/login', data={
		'username': test_user['email'],
		'password': test_user['password']
	})
	log_response = schemas.Token(**response.json())
	payload = jwt.decode(log_response.access_token, settings.secret_key, algorithms=[settings.algorithm])
	id: str = payload.get('user_id')
	assert response.status_code == 200
	assert id == test_user['id']
	assert log_response.token_type == 'bearer'

'''
@pytest.mark.parametrize('email, password, status_code',[
	('pepe@gmail.com', 'testPassword123', 403),
	('test@gmail.com', 'incorrect_password', 403),
	(None, 'testPassword123', 422),
	('test@gmail.com', None, 422),
	('pepe@gmail.com', 'incorrect_password', 403)
])
async def test_incorrect_login(client, test_user, email, password, status_code):
	response = await client.post('/login', data={
		'username': email,
		'password': password
	})

	assert response.status_code == status_code
'''