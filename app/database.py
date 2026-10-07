# ruff: noqa: I001
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
import os

load_dotenv()
database_url = os.getenv("SQLALCHEMY_DATABASE_URL")

# SQLAlchemy is the ORM (Object Relational Mapper) that connects one web service to the database
# In our case; we are connecting FastAPI to PostgreSQL via SQLAlchemy.
# This eliminates the use of writing hardcode SQL queries to access the database
# With ORMs, you can write Python code which converts into SQL BTS and executes the required queries

# The engine is responsible to create the connxn between your API and database
engine = create_engine(database_url)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

# Up until now is the stock code that you will use in each project where SQLAlchemy is used except that the URLs will be different


# A dependency needed to get the database in the main file to use alongwith the ORM
# The session object is responsible to create a connxn with the database
# So the idea is everytime we get a request, we'll start a session, once fulfilled; we close it off.
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()