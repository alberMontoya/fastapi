from datetime import datetime
from pydantic import BaseModel, ConfigDict


class PostBase(BaseModel):
	title: str
	content: str
	published: bool = True
	
class PostCreate(PostBase):
	pass

class PostResponse(PostBase):
	id: int
	created_at: datetime
	
	model_config = ConfigDict(
		# ANTES: orm_mode = True, para mapear el objeto del modelo orm con este
        from_attributes=True  
    )

	