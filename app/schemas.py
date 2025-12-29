from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict, EmailStr, Field, conint


class UserCreate(BaseModel):
	email: EmailStr
	password: str

class UserOut(BaseModel):
	id: int
	email: EmailStr
	created_at: datetime
	
	model_config = ConfigDict(
		# ANTES: orm_mode = True, para mapear el objeto del modelo orm con este
        from_attributes=True  
    )

class UserLogin(BaseModel):
	email: EmailStr
	password: str

class PostBase(BaseModel):
	title: str
	content: str
	published: bool = True
	
class PostCreate(PostBase):
	pass

class PostResponse(PostBase):
	id: int
	created_at: datetime
	user_id: int
	owner: UserOut
	
	model_config = ConfigDict(
		# ANTES: orm_mode = True, para mapear el objeto del modelo orm con este
        from_attributes=True  
    )

class PostVotes(BaseModel):
	"""
	Post en uppercase porque asi lo devolvera la query en la tupla
	"""
	Post: PostResponse
	votes: int

	model_config = ConfigDict(
		# ANTES: orm_mode = True, para mapear el objeto del modelo orm con este
        from_attributes=True  
    )

class Token(BaseModel):
	access_token: str
	token_type: str

class TokenData(BaseModel):
	id: Optional[str] = None

class Vote(BaseModel):
	post_id: int
	dir: int = Field(ge=0, le=1)