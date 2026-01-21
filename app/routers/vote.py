from typing import List, Optional
from fastapi import Depends,  Response, status, HTTPException, APIRouter
from app import models, schemas, oauth2
from ..database import get_db
from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter(
	prefix="/vote",
	tags=['Vote']
)

@router.post('', status_code=status.HTTP_201_CREATED)
async def vote(vote: schemas.Vote, db:AsyncSession = Depends(get_db), 
		 get_current_user: int = Depends(oauth2.get_current_user)):
	
	stmt_post = select(models.Post).where(models.Post.id == vote.post_id)
	existing_post = (await db.execute(stmt_post)).scalar_one_or_none()
	if not existing_post:
		raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post doesnt exist")
	
	vote_query = select(models.Vote).where(models.Vote.post_id == vote.post_id,
							   models.Vote.user_id == get_current_user.id)
	query_result = (await db.execute(vote_query)).scalar_one_or_none()
	try:
		if vote.dir == 1:
			if query_result:
				raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f"Post already voted by this user")
			new_vote = models.Vote(post_id = vote.post_id, user_id = get_current_user.id)
			db.add(new_vote)
			await db.commit()

			return {"status": "successfully added vote"}
		else:
			if not query_result:
				raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Vote doesnt exist")
			
			delete_stmt = delete(models.Vote).where(models.Vote.post_id == vote.post_id,
							   models.Vote.user_id == get_current_user.id)
			await db.execute(delete_stmt)
			await db.commit()

			return {"status": "successfully deleted vote"}
	except:
		await db.rollback()
		raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while voting the post"
        )