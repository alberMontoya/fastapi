from fastapi import APIRouter, Depends, status, HTTPException, Response
from sqlalchemy.orm import Session
from fastapi.security.oauth2 import OAuth2PasswordRequestForm
from app import schemas, database, models, utils, oauth2




router = APIRouter(tags=['Authentication'])

@router.post('/login', response_model=schemas.Token)
def login(user_credentials: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(database.get_db)):
	user = db.query(models.User).filter(user_credentials.username == models.User.email).first()

	if not user:
		raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='Invalid credentials')
	
	if not utils.verify(user_credentials.password, user.password):
		raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='Invalid credentials')
	
	#create a JWT token
	data = {"user_id": user.id}
	access_token = oauth2.create_access_token(data)

	return {"access_token": access_token, "token_type": "bearer"}
