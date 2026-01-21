from .config import settings
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from typing import AsyncGenerator

#dialect+driver://user:password@host:port/database_name
#motorbbdd://<user>:<password>@<ip>/<bbdd_name>

SQLALCHEMY_DATABASE_URL =f'postgresql+asyncpg://{settings.database_username}:{settings.database_password}@{settings.database_hostname}/{settings.database_name}'

engine = create_async_engine(SQLALCHEMY_DATABASE_URL, echo=True)

SessionLocal = async_sessionmaker(autocommit=False, autoflush=False, bind=engine)

async def get_db() -> AsyncGenerator[AsyncSession, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        await db.close()
'''def get_db():
	db = SessionLocal()
	try:
		yield db
	finally:
		db.close()
'''

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