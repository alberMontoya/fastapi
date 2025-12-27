from .database import Base
from sqlalchemy import Column, Integer, String, Boolean, ForeignKey
from sqlalchemy.sql.sqltypes import TIMESTAMP
from sqlalchemy.sql.expression import text
from sqlalchemy.orm import relationship

class Post(Base):
	__tablename__ = "posts"

	id = Column(Integer, primary_key=True, nullable=False)
	user_id = Column(Integer, ForeignKey('user.id', ondelete='CASCADE'), nullable=False)
	title = Column(String, nullable=False)
	content = Column(String, nullable=False)
	published = Column(Boolean, server_default='TRUE', nullable=False)
	created_at = Column(TIMESTAMP(timezone=True), nullable=False, 
						server_default=text('now()'))
	owner = relationship("User")
	
class User(Base):
	__tablename__ = "user"

	id = Column(Integer, primary_key=True, nullable=False)
	email = Column(String, nullable=False, unique=True)
	password = Column(String, nullable=False)
	created_at = Column(TIMESTAMP(timezone=True), nullable=False, 
						server_default=text('now()'))