from random import randrange
from typing import Optional
from fastapi import FastAPI, Response, status, HTTPException
from fastapi.params import Body
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import psycopg2
from psycopg2.extras import RealDictCursor


app = FastAPI()

class Post(BaseModel):
	title: str
	content: str
	published: bool = True

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

@app.get('/posts')
def get_posts():
	cursor.execute('''SELECT * FROM posts''')
	posts = cursor.fetchall()
	print(posts)
	return {"data": posts}

@app.post('/posts', status_code=status.HTTP_201_CREATED)
def create_post(new_post: Post):
	cursor.execute('''INSERT INTO posts (title, content, published) VALUES
		(%s, %s, %s) RETURNING *''', (new_post.title, new_post.content, new_post.published))
	inserted_post = cursor.fetchone()
	conn.commit()
	return {"data": inserted_post}
	

@app.get('/posts/latest')
def get_latest_post():
	'''el orden importa, si este endpoint está después del get_post, fastapi va a 
	intentar matchear latest como el {id} y dará un error'''
	return my_posts[-1]

@app.get('/posts/{id}')
def get_post(id: int):
	#id tiene que ser str para que no cree conflictos %s
	cursor.execute('''SELECT * FROM posts WHERE id=%s''', (str(id)))
	post = cursor.fetchone()
	if not post:
		raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Item {id} not found")
	
	return {"post_detail": post}


@app.delete('/posts/{id}', status_code=status.HTTP_204_NO_CONTENT)
def delete_post(id: int):
	cursor.execute(''' DELETE FROM posts WHERE id = %s RETURNING *''', (str(id)))
	deleted_post = cursor.fetchone()
	conn.commit()
	if not deleted_post:
		raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Item {id} not found")
	
	#no queremos devolver nada, para delete status 204
	return Response(status_code=status.HTTP_204_NO_CONTENT)

@app.put('/posts/{id}')
def update_post(id: int, post: Post):
	cursor.execute('''UPDATE posts SET title = %s,
				content = %s,
				published = %s
				WHERE id = %s RETURNING *''', 
				(post.title, post.content, post.published, str(id)))
	updated_post = cursor.fetchone()
	#commit siempre que hagamos cambios en bbdd (insert, delete, update)
	conn.commit()
	if not updated_post:
		raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Item {id} not found")
	
	return {"data": updated_post}