from sqlalchemy import Column, Integer, String, Boolean, ForeignKey
from sqlalchemy.sql.sqltypes import TIMESTAMP
from sqlalchemy.sql.expression import text
from sqlalchemy.orm import relationship, DeclarativeBase, Mapped, mapped_column
from datetime import datetime

class Base(DeclarativeBase):
	pass

class Post(Base):
	__tablename__ = "posts"

	id: Mapped[int] = mapped_column(Integer, primary_key=True, nullable=False)
	user_id: Mapped[int] = mapped_column(Integer, ForeignKey('user.id', ondelete='CASCADE'), nullable=False)
	title: Mapped[str] = mapped_column(String(255), nullable=False)
	content: Mapped[str] = mapped_column(String(140), nullable=False)
	published: Mapped[bool] = mapped_column(Boolean, server_default='TRUE', nullable=False)
	created_at: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), nullable=False, 
						server_default=text('now()'))
	owner: Mapped["User"] = relationship("User")

	def __repr__(self):
		return f"Post(id={self.id!r}, user_id={self.user_id!r}), title={self.title!r}, content={self.content!r}, \
			published={self.published!r}, created_at={self.created_at!r}, owner={self.owner!r}"
	
class User(Base):
	__tablename__ = "user"

	id: Mapped[int] = mapped_column(Integer, primary_key=True, nullable=False)
	email: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)
	password: Mapped[str] = mapped_column(String(255), nullable=False)
	created_at: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), nullable=False, 
						server_default=text('now()'))
	def __repr__(self):
		return f"User(id={self.id!r}, email={self.email!r}, created_at={self.created_at!r})"
class Vote(Base):
	__tablename__ = "votes"

	post_id: Mapped[int] = mapped_column(Integer, ForeignKey('posts.id', ondelete='CASCADE'), primary_key=True, nullable=False)
	user_id: Mapped[int] = mapped_column(Integer, ForeignKey('user.id', ondelete='CASCADE'), primary_key=True, nullable=False)

	def __repr__(self):
		return f"Vote(post_id={self.post_id!r}, user_id={self.user_id!r})"