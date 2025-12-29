from typing import List, Optional
from fastapi import Depends,  Response, status, HTTPException, APIRouter
from sqlalchemy.orm import Session
from app import models, schemas, oauth2
from ..database import get_db
from sqlalchemy import func

router = APIRouter(
	prefix="/posts",
	tags=['Posts']
)

@router.get('/', response_model=List[schemas.PostVotes])
def get_posts(db:Session = Depends(get_db),  
			  get_current_user: int = Depends(oauth2.get_current_user),
			  limit: int = 10,
			  skip: int = 0):
	# cursor.execute('''SELECT * FROM posts''')
	# posts = cursor.fetchall()
	#query parameter
	print(limit)
	#posts = db.query(models.Post).limit(limit).offset(skip).all()
	#print(posts)
	"""
	post_votes devuelve una tupla (models.Post, votes). La clase schemas.PostVotes validara
	el primer parametro como un PostResponse(en mayuscula en el esquema porque asi
	lo intentara validar pydantic) y el segundo como un int
	"""
	post_votes = db.query(models.Post, func.count(models.Vote.post_id).label("votes")).join(
		models.Vote, models.Vote.post_id == models.Post.id, isouter=True).group_by(models.Post.id).limit(limit).offset(skip).all()
	return post_votes

@router.post('/', status_code=status.HTTP_201_CREATED, response_model=schemas.PostResponse)
def create_post(new_post: schemas.PostCreate, db:Session = Depends(get_db), get_current_user: int = Depends(oauth2.get_current_user)):
	# cursor.execute('''INSERT INTO posts (title, content, published) VALUES
	# 	(%s, %s, %s) RETURNING *''', (new_post.title, new_post.content, new_post.published))
	# inserted_post = cursor.fetchone()
	# conn.commit()
	#new_post.model_dump() lo pasa a dict
	print(get_current_user.id)
	post_info = new_post.model_dump()
	post_info.update({"user_id": get_current_user.id})
	inserted_post = models.Post(**post_info)
	db.add(inserted_post)
	db.commit()
	#recupera el elemento insertado en el commit y se lo da
	#a la variable que se lo pasa
	db.refresh(inserted_post)
	return inserted_post
	
@router.get('/{id}', response_model=schemas.PostVotes)
def get_post(id: int, db:Session = Depends(get_db)):
	#id tiene que ser str para que no cree conflictos %s
	# cursor.execute('''SELECT * FROM posts WHERE id=%s''', (str(id)))
	# post = cursor.fetchone()
	# if not post:
	# 	raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Item {id} not found")
	post = db.query(models.Post, func.count(models.Vote.post_id).label("votes")).join(
		models.Vote, models.Vote.post_id == models.Post.id, isouter=True).group_by(models.Post.id).filter(
			models.Post.id == id
		).first()
	if not post:
		raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Item {id} not found")
	
	return post


@router.delete('/{id}', status_code=status.HTTP_204_NO_CONTENT)
def delete_post(id: int, db:Session = Depends(get_db), get_current_user: int = Depends(oauth2.get_current_user)):
	# cursor.execute(''' DELETE FROM posts WHERE id = %s RETURNING *''', (str(id)))
	# deleted_post = cursor.fetchone()
	# conn.commit()
	post = db.query(models.Post).filter(
			models.Post.id == id
		)

	post_first = post.first() 
	if not post_first:
		raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Item {id} not found")
	
	if post_first.user_id != get_current_user.id:
		raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=f"Not authorized to perform this action")
	
	post.delete(synchronize_session=False)
	db.commit()
	#no queremos devolver nada, para delete status 204
	return Response(status_code=status.HTTP_204_NO_CONTENT)

@router.put('/{id}', response_model=schemas.PostResponse)
def update_post(id: int, post: schemas.PostCreate, db:Session = Depends(get_db), get_current_user: int = Depends(oauth2.get_current_user)):
	# cursor.execute('''UPDATE posts SET title = %s,
	# 			content = %s,
	# 			published = %s
	# 			WHERE id = %s RETURNING *''', 
	# 			(post.title, post.content, post.published, str(id)))
	# updated_post = cursor.fetchone()
	# #commit siempre que hagamos cambios en bbdd (insert, delete, update)
	# conn.commit()

	post_query = db.query(models.Post).filter(
			models.Post.id == id
		)
	print(post_query)

	post_first = post_query.first() 
	if not post_first:
		raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Item {id} not found")
	
	if post_first.user_id != get_current_user.id:
		raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=f"Not authorized to perform this action")
	
	post_query.update(post.model_dump(), synchronize_session=False)
	db.commit()
	
	return post_query.first()