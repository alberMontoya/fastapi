from typing import List
from fastapi import Depends,  Response, status, HTTPException, APIRouter
from sqlalchemy.orm import Session
from app import models, schemas, utils
from ..database import get_db

router = APIRouter(
	prefix="/user",
	tags=['Users']
)

@router.post('/', status_code=status.HTTP_201_CREATED, response_model=schemas.UserOut)
def create_user(user: schemas.UserCreate, db:Session = Depends(get_db)):
	#hash the password -> user.password
	hashed_password = utils.hash(user.password)
	user.password = hashed_password
	inserted_user = models.User(**user.model_dump())
	db.add(inserted_user)
	db.commit()
	db.refresh(inserted_user)
	return inserted_user

@router.get('/{id}', response_model=schemas.UserOut)
def get_user(id: int, db:Session = Depends(get_db)):
	query = db.query(models.User).filter(models.User.id == id).first()

	if not query:
		raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"User with {id} not found")
	
	return query