from datetime import datetime, timedelta, timezone
import jwt
from jwt import PyJWTError, encode
from jwt.exceptions import InvalidTokenError
from app import schemas, database, models
from fastapi import Depends, status, HTTPException
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy import select
from .config import settings
from sqlalchemy.ext.asyncio import AsyncSession


oauth2_scheme = OAuth2PasswordBearer(tokenUrl='login')

#SECRET KEY (openssl rand -hex 32)
SECRET_KEY = settings.secret_key
#ALGORITHM
ALGORITHM = settings.algorithm
#EXPIRATION TIME
ACCESS_TOKEN_EXPIRE_MINUTES = settings.access_token_expire_minutes


def create_access_token(data: dict, expires_delta: timedelta | None = None):
	to_encode = data.copy()

	if expires_delta:
		expire = datetime.now(timezone.utc) + timedelta(minutes = expires_delta)
	else:
		expire = datetime.now(timezone.utc) + timedelta(minutes = ACCESS_TOKEN_EXPIRE_MINUTES)

	to_encode.update({"exp": expire})

	encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
	return encoded_jwt

def verify_access_token(token: str, credentials_exception):
	try:
		payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])

		id: str = payload.get("user_id")

		if not id:
			raise credentials_exception
		
		token_data = schemas.TokenData(id=str(id))
	except PyJWTError:
		raise credentials_exception
	
	return token_data
	
async def get_current_user(token: str = Depends(oauth2_scheme), db: AsyncSession = Depends(database.get_db)):
	credentials_exception = HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, 
		detail=f"Could not validate credentials", headers={"WWW-Authenticate": "Bearer"})
	
	token = verify_access_token(token, credentials_exception)

	stmt = select(models.User).where(models.User.id == int(token.id))
	user = (await db.execute(stmt)).scalar_one_or_none()

	return user

	
	
