from fastapi import APIRouter, Depends, status, HTTPException, Response
from fastapi.security.oauth2 import OAuth2PasswordRequestForm
from app import schemas, database, models, utils, oauth2
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession




router = APIRouter(tags=['Authentication'])

@router.post('/login', response_model=schemas.Token)
async def login(user_credentials: OAuth2PasswordRequestForm = Depends(), db: AsyncSession = Depends(database.get_db)):
	stmt = select(models.User).where(user_credentials.username == models.User.email)
	user = (await db.execute(stmt)).scalar_one_or_none()

	if not user or not utils.verify(user_credentials.password, user.password):
		raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Invalid credentials')
	
	#create a JWT token
	data = {"user_id": user.id}
	access_token = oauth2.create_access_token(data)

	return {"access_token": access_token, "token_type": "bearer"}
