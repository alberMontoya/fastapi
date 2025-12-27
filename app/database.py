from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from .config import settings

#dialect+driver://user:password@host:port/database_name
#motorbbdd://<user>:<password>@<ip>/<bbdd_name>
SQLALCHEMY_DATABASE_URL =f'postgresql://{settings.database_username}:{settings.database_password}@{settings.database_hostname}/{settings.database_name}'

engine = create_engine(SQLALCHEMY_DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
	db = SessionLocal()
	try:
		yield db
	finally:
		db.close()

"""con psycopg:
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
"""