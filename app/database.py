from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

#dialect+driver://user:password@host:port/database_name
#motorbbdd://<user>:<password>@<ip>/<bbdd_name>
SQLALCHEMY_DATABASE_URL ='postgresql://postgres:172498@localhost/fastapi'

engine = create_engine(SQLALCHEMY_DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
	db = SessionLocal()
	try:
		yield db
	finally:
		db.close()