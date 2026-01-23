from typing import List, Optional
from fastapi import Depends,  Response, status, HTTPException, APIRouter
from sqlalchemy.orm import selectinload
from app import models, schemas, oauth2
from ..database import get_db
from sqlalchemy import func, select, delete, update
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter(
	prefix="/posts",
	tags=['Posts']
)

@router.get('', response_model=List[schemas.PostVotes])
async def get_posts(db:AsyncSession = Depends(get_db),  
			  get_current_user: int = Depends(oauth2.get_current_user),
			  limit: int = 10,
			  skip: int = 0):
	# cursor.execute('''SELECT * FROM posts''')
	# posts = cursor.fetchall()
	#query parameter
	#print(limit)
	#posts = db.query(models.Post).limit(limit).offset(skip).all()
	#print(posts)
	"""
	post_votes devuelve una tupla (models.Post, votes). La clase schemas.PostVotes validara
	el primer parametro como un PostResponse(en mayuscula en el esquema porque asi
	lo intentara validar pydantic) y el segundo como un int
	"""
	stmt = select(models.Post, func.count(models.Vote.post_id).label("votes")).join(
		models.Vote, models.Vote.post_id == models.Post.id, isouter=True).group_by(models.Post.id).limit(limit).offset(skip)
	result = (await db.execute(stmt)).all()
	return result

@router.post('', status_code=status.HTTP_201_CREATED, response_model=schemas.PostResponse)
async def create_post(new_post: schemas.PostCreate, db:AsyncSession = Depends(get_db), get_current_user: int = Depends(oauth2.get_current_user)):
	# cursor.execute('''INSERT INTO posts (title, content, published) VALUES
	# 	(%s, %s, %s) RETURNING *''', (new_post.title, new_post.content, new_post.published))
	# inserted_post = cursor.fetchone()
	# conn.commit()
	#new_post.model_dump() lo pasa a dict
	try:
		print(get_current_user.id)
		post_info = new_post.model_dump()
		post_info.update({"user_id": get_current_user.id})
		inserted_post = models.Post(**post_info)
		db.add(inserted_post)
		await db.flush()
		#recupera el elemento insertado en el commit y se lo da
		#a la variable que se lo pasa
		await db.refresh(inserted_post, attribute_names=["owner"]) #para la relationship
		await db.commit()
		
		return inserted_post
	except:
		await db.rollback()
		raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while creating the post"
        )
	
@router.get('/{id}', response_model=schemas.PostVotes)
async def get_post(id: int, db:AsyncSession = Depends(get_db)):
	#id tiene que ser str para que no cree conflictos %s
	# cursor.execute('''SELECT * FROM posts WHERE id=%s''', (str(id)))
	# post = cursor.fetchone()
	# if not post:
	# 	raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Item {id} not found")
	#selectinload para cargar la relationship
	stmt = select(models.Post, func.count(models.Vote.post_id).label("votes")).join(
		models.Vote, models.Vote.post_id == models.Post.id, isouter=True).options(selectinload(models.Post.owner)).group_by(models.Post.id).where(
			models.Post.id == id
		)
	post = (await db.execute(stmt)).one_or_none()
	if not post:
		raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Item {id} not found")
	
	return post


@router.delete('/{id}', status_code=status.HTTP_204_NO_CONTENT)
async def delete_post(id: int, db:AsyncSession = Depends(get_db), get_current_user: int = Depends(oauth2.get_current_user)):
	# cursor.execute(''' DELETE FROM posts WHERE id = %s RETURNING *''', (str(id)))
	# deleted_post = cursor.fetchone()
	# conn.commit()
	try:
		post = select(models.Post).where(models.Post.id == id)

		post_first = (await db.execute(post)).scalar_one_or_none() 
		if not post_first:
			raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Item {id} not found")
		
		if post_first.user_id != get_current_user.id:
			raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=f"Not authorized to perform this action")
		
		to_delete = delete(models.Post).where(models.Post.id == id)
		await db.execute(to_delete)
		await db.commit()
		#no queremos devolver nada, para delete status 204
		return Response(status_code=status.HTTP_204_NO_CONTENT)
	except:
		await db.rollback()
		raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while deleting the post"
        )

@router.put('/{id}', response_model=schemas.PostResponse)
async def update_post(id: int, post: schemas.PostCreate, db:AsyncSession = Depends(get_db), get_current_user: int = Depends(oauth2.get_current_user)):
	# cursor.execute('''UPDATE posts SET title = %s,
	# 			content = %s,
	# 			published = %s
	# 			WHERE id = %s RETURNING *''', 
	# 			(post.title, post.content, post.published, str(id)))
	# updated_post = cursor.fetchone()
	# #commit siempre que hagamos cambios en bbdd (insert, delete, update)
	# conn.commit()
	try:
		# 1. Buscamos el post incluyendo al owner para la validación final
		post_query = select(models.Post).options(selectinload(models.Post.owner)).where(models.Post.id == id)

		post_first = (await db.execute(post_query)).scalar_one_or_none()

		if not post_first:
			raise HTTPException(status_code=404, detail=f"Item {id} not found")

		if post_first.user_id != get_current_user.id:
			raise HTTPException(status_code=403, detail="Not authorized")

		to_update = update(models.Post).where(models.Post.id == id).values(**post.model_dump()).returning(models.Post)
		result = (await db.execute(to_update)).scalar_one_or_none()
        
		await db.commit()
		await db.refresh(result, attribute_names=["owner"])

		return result
	except:
		await db.rollback()
		raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while updating the post"
        )