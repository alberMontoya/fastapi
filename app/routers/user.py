from typing import List
from fastapi import Depends,  Response, status, HTTPException, APIRouter
from app import models, schemas, utils
from ..database import get_db
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter(
	prefix="/user",
	tags=['Users']
)

@router.post('', status_code=status.HTTP_201_CREATED, response_model=schemas.UserOut)
async def create_user(user: schemas.UserCreate, db:AsyncSession = Depends(get_db)):
	try:
		#hash the password -> user.password
		hashed_password = utils.hash(user.password)
		user.password = hashed_password
		inserted_user = models.User(**user.model_dump())
		db.add(inserted_user)
		await db.commit()
		await db.refresh(inserted_user)
		return inserted_user
	except:
		await db.rollback()
		raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while creating the user"
        )

@router.get('/{id}', response_model=schemas.UserOut)
async def get_user(id: int, db:AsyncSession = Depends(get_db)):
	stmt = select(models.User).where(models.User.id == id)
	query = (await db.execute(stmt)).scalar_one_or_none()
	
	if not query:
		raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"User with {id} not found")
	
	return query