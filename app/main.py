from random import randrange
from typing import Optional, List
from fastapi import Depends, FastAPI, Response, status, HTTPException
from fastapi.params import Body
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import psycopg2
from psycopg2.extras import RealDictCursor
from sqlalchemy.orm import Session
from app import models, schemas
from .database import engine, SessionLocal, get_db


models.Base.metadata.create_all(bind=engine)

app = FastAPI()

try:
	conn = psycopg2.connect(host='localhost', database='fastapi', user = 'postgres',
						password='172498', client_encoding='utf8', 
						cursor_factory=RealDictCursor)
	cursor = conn.cursor()
	print("Database connection OK")
except Exception as error:
	print("Connecting to database failed")
	print(f"Error: {error}")
	exit(1)
		

my_posts = [
	{'title': 'First Post', 'content': 'This is the first post', 'id': 1},
	{'title': 'Second Post', 'content': 'This is the second post', 'id': 2},]

def find_post(id: int):
	for item in my_posts:
		print(item)
		if id == item['id']:
			return item
	return -1

def find_index_post(id:int):
	for i, p in enumerate(my_posts):
		if id == p['id']:
			return i
	return -1


@app.get('/')
async def index():
	return{'hello': 'world'}

@app.get('/posts', response_model=List[schemas.PostResponse])
def get_posts(db:Session = Depends(get_db)):
	# cursor.execute('''SELECT * FROM posts''')
	# posts = cursor.fetchall()
	posts = db.query(models.Post).all()
	#print(posts)
	return posts

@app.post('/posts', status_code=status.HTTP_201_CREATED, response_model=schemas.PostResponse)
def create_post(new_post: schemas.PostCreate, db:Session = Depends(get_db)):
	# cursor.execute('''INSERT INTO posts (title, content, published) VALUES
	# 	(%s, %s, %s) RETURNING *''', (new_post.title, new_post.content, new_post.published))
	# inserted_post = cursor.fetchone()
	# conn.commit()
	#new_post.model_dump() lo pasa a dict
	inserted_post = models.Post(**new_post.model_dump())
	db.add(inserted_post)
	db.commit()
	#recupera el elemento insertado en el commit y se lo da
	#a la variable que se lo pasa
	db.refresh(inserted_post)
	return inserted_post
	
@app.get('/posts/{id}', response_model=schemas.PostResponse)
def get_post(id: int, db:Session = Depends(get_db)):
	#id tiene que ser str para que no cree conflictos %s
	# cursor.execute('''SELECT * FROM posts WHERE id=%s''', (str(id)))
	# post = cursor.fetchone()
	# if not post:
	# 	raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Item {id} not found")
	post = db.query(models.Post).filter(
			models.Post.id == id
		).first()
	if not post:
		raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Item {id} not found")
	
	return post


@app.delete('/posts/{id}', status_code=status.HTTP_204_NO_CONTENT)
def delete_post(id: int, db:Session = Depends(get_db)):
	# cursor.execute(''' DELETE FROM posts WHERE id = %s RETURNING *''', (str(id)))
	# deleted_post = cursor.fetchone()
	# conn.commit()
	post = db.query(models.Post).filter(
			models.Post.id == id
		)

	if not post.first():
		raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Item {id} not found")
	
	post.delete(synchronize_session=False)
	db.commit()
	#no queremos devolver nada, para delete status 204
	return Response(status_code=status.HTTP_204_NO_CONTENT)

@app.put('/posts/{id}', response_model=schemas.PostResponse)
def update_post(id: int, post: schemas.PostCreate, db:Session = Depends(get_db)):
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
	if not post_query.first():
		raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Item {id} not found")
	
	post_query.update(post.model_dump(), synchronize_session=False)
	db.commit()
	
	return post_query.first()