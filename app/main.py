from typing import Optional
from fastapi import FastAPI, Response, status, HTTPException
from fastapi.params import Body
from fastapi.responses import JSONResponse
from pydantic import BaseModel

app = FastAPI()

class Post(BaseModel):
	title: str
	content: str
	published: bool = True
	rating: Optional[int] = None

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
	return {"data": my_posts}

@app.post('/posts', status_code=status.HTTP_201_CREATED)
async def create_post(new_post: Post):
	#pasa el objeto de Post a un diccionario
	print(new_post.model_dump())
	if new_post.model_dump().get('id') is None:
		aux_post = new_post.model_dump()
		aux_post['id'] = len(my_posts) + 1
		my_posts.append(aux_post)
	else:
		my_posts.append(new_post.model_dump())
	
	return {
		'message': 'Post created successfully',
		'total posts': my_posts
	}

@app.get('/posts/latest')
def get_latest_post():
	'''el orden importa, si este endpoint está después del get_post, fastapi va a 
	intentar matchear latest como el {id} y dará un error'''
	return my_posts[-1]

@app.get('/posts/{id}')
def get_post(id: int):
	aux = find_post(id)
	print(type(aux))
	if aux == -1:
		raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Item {id} not found")
		
	return aux

@app.delete('/posts/{id}', status_code=status.HTTP_204_NO_CONTENT)
def delete_post(id: int):
	aux_index = find_index_post(id)
	if aux_index == -1:
		raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Item {id} not found")
	#my_posts.pop(aux_index)
	del my_posts[aux_index]
	#no queremos devolver nada, para delete status 204
	return Response(status_code=status.HTTP_204_NO_CONTENT)

@app.put('/posts/{id}')
def update_post(id: int, post: Post):
	print(post)
	aux_index = find_index_post(id)
	if aux_index == -1:
		raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Item {id} not found")
	
	post_dict = post.model_dump()
	post_dict['id'] = id
	my_posts[aux_index] = post_dict
	return {"data": post_dict}