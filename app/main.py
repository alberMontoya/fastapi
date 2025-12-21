from fastapi import Depends, FastAPI
import psycopg2
from psycopg2.extras import RealDictCursor
from app import models
from .database import engine
from .routers import post, user, auth


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
def root():
	return {"hello": "world"}

app.include_router(post.router)
app.include_router(user.router)
app.include_router(auth.router)