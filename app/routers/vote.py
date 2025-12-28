from typing import List, Optional
from fastapi import Depends,  Response, status, HTTPException, APIRouter
from sqlalchemy.orm import Session
from app import models, schemas, oauth2
from ..database import get_db

router = APIRouter(
	prefix="/vote",
	tags=['Vote']
)

@router.post("/", status_code=status.HTTP_201_CREATED)
def vote(vote: schemas.Vote, db:Session = Depends(get_db), 
		 get_current_user: int = Depends(oauth2.get_current_user)):
	
	existing_post = db.query(models.Post).filter(models.Post.id == vote.post_id).first()
	if not existing_post:
		raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post doesnt exist")
	
	vote_query = db.query(models.Vote).filter(models.Vote.post_id == vote.post_id,
							   models.Vote.user_id == get_current_user.id)
	query_result = vote_query.first()
	if vote.dir == 1:
		if query_result:
			raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f"Post already voted by this user")
		new_vote = models.Vote(post_id = vote.post_id, user_id = get_current_user.id)
		db.add(new_vote)
		db.commit()

		return {"status": "successfully added vote"}
	else:
		if not query_result:
			raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Vote doesnt exist")
		
		vote_query.delete(synchronize_session=False)
		db.commit()

		return {"status": "successfully deleted vote"}