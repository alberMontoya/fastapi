from typing import List
from fastapi import Depends,  Response, status, HTTPException, APIRouter
from app import models, schemas, utils
from ..database import get_db
from sqlalchemy import select, exc
from sqlalchemy.ext.asyncio import AsyncSession
import sys

router = APIRouter(
	prefix="/user",
	tags=['Users']
)

@router.post('', status_code=status.HTTP_201_CREATED, response_model=schemas.UserOut)
async def create_user(user: schemas.UserCreate, db:AsyncSession = Depends(get_db)):
	
	try:
		hashed_password = utils.hash(user.password)
		user_data = user.model_dump()
		user_data["password"] = hashed_password

		new_user = models.User(**user_data)
		db.add(new_user)
		await db.commit()
		# Intentamos el refresh
		await db.refresh(new_user)
		return new_user
		
	except exc.SQLAlchemyError as e:
		await db.rollback()
		print(f"--- ERROR DE SQLALCHEMY: {e} ---", file=sys.stderr)
		raise HTTPException(status_code=400, detail=str(e))
	except Exception as e:
		await db.rollback()
		print(f"--- ERROR INESPERADO: {type(e).__name__}: {e} ---", file=sys.stderr)
		raise HTTPException(status_code=500, detail=f"Error interno: {type(e).__name__}")

@router.get('/{id}', response_model=schemas.UserOut)
async def get_user(id: int, db:AsyncSession = Depends(get_db)):
	stmt = select(models.User).where(models.User.id == id)
	query = (await db.execute(stmt)).scalar_one_or_none()
	
	if not query:
		raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"User with {id} not found")
	
	return query