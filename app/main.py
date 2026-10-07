# ruff: noqa: I001
from fastapi import FastAPI, Response, status, HTTPException, Depends
from pydantic import BaseModel
import psycopg
from sqlalchemy.orm import Session
from psycopg.rows import dict_row
import os
from dotenv import load_dotenv
import time
from . import models, schemas
from .database import engine, get_db

#once the application reruns, the line of code creates all the tables we have in our models.py file
#so 'posts' should already be created
models.Base.metadata.create_all(bind=engine)
db_dependency = Depends(get_db)

# Getting the database url for initiating a connection to our database
load_dotenv()
database_url = os.getenv("DATABASE_URL")

if not database_url:
    raise RuntimeError("DATABASE_URL is missing")

# Creating an instance of FastAPI
app = FastAPI()



# Actual code to connect to our database
while True:
    try:
        conn = psycopg.connect(database_url, row_factory=dict_row)
        cur = conn.cursor()
        print("DB connection was successful!")
        break
    except psycopg.OperationalError as e:
        print(f"Could not connect to the database: {e}")
        time.sleep(2)


# uvicorn main:app --reload should only be used in a development environment; we don't want to constantly change our production environment and hence all the constant changes that happen here should occur only during the development phase.

my_posts = [
    {"title": "title of post 1", "content": "content of post 1", "id": 1},
    {"title": "Favorite Foods", "content": "I like pizza", "id": 2},
]


def find_post(id):
    for p in my_posts:
        if p["id"] == id:
            return p


def find_index_post(id):
    for i, p in enumerate(my_posts):
        if p["id"] == id:
            return i


# A path operation with 2 components : a function and a decorator
# This decorator turns the regular function into a path operation
# The get method takes the root() function and calls the get method at / and provides us the results on the server endpoint
# Method -> Path -> Function
@app.get("/")
def root():  # a regular function that returns a JSON object
    message = "Hello World"
    return {"message": message}


# @app.get("/sqlalchemy")
# def test_posts(db: Session = Depends(get_db)):
#     posts = db.query(models.Post).all()
#     return {"data": posts}


@app.get("/posts")
def get_posts(db: Session = db_dependency):
    # cur.execute("""SELECT * FROM posts;""")
    # posts = cur.fetchall()
    posts = db.query(models.Post).all()
    return {"data": posts}


@app.get(
    "/posts/{id}"
)  # id here is a path parameter; representing the id of a specific post
def get_post(id: int, db: Session = db_dependency):
    # cur.execute("""SELECT * FROM posts WHERE pid = %s""", (id,))
    # post = cur.fetchone()
    
    post = db.query(models.Post).filter(models.Post.id == id).first()
    if post is None:
        # response.status_code = status.HTTP_404_NOT_FOUND
        # return {"message" : f"Post with id: {id} was not found"}
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Post with id: {id} was not found",
        )
    return {"post_detail": post}


@app.post("/posts", status_code=status.HTTP_201_CREATED)
def create_post(post: schemas.PostCreate, db: Session = db_dependency):
    # cur.execute(
    #     """INSERT INTO posts (title, content, published) VALUES (%s, %s, %s) RETURNING *""",
    #     (post.title, post.content, post.published),
    # )
    # new_post = cur.fetchone()
    # conn.commit()
    new_post = models.Post(**post.model_dump())
    db.add(new_post)
    db.commit()
    db.refresh(new_post)
    return {
        "data": new_post
    }  # We usually do not send the data back to the user; we save it inside a database. That's how any application works


# For this project; we are going to save the post in memory.
# What kind of schema do we want for the POST request
# We want a title: str, content: str


@app.delete("/posts/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_post(id: int, db: Session = db_dependency):

    # cur.execute("""DELETE FROM posts WHERE pid = %s RETURNING *""", (id,))
    # deleted_post = cur.fetchone()
    # conn.commit()
    deleted_post = db.query(models.Post).filter(models.Post.id == id).first()
    if deleted_post is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Post with id: {id} was not found",
        )

    db.delete(deleted_post)
    db.commit()

    return Response(status_code=status.HTTP_204_NO_CONTENT)


@app.put("/posts/{id}")
def update_post(id: int, post: schemas.PostBase, db: Session = db_dependency):
    # cur.execute(
    #     """UPDATE posts SET title = %s, content = %s, published = %s WHERE pid = %s RETURNING *""",
    #     (
    #         post.title,
    #         post.content,
    #         post.published,
    #         id,
    #     ),
    # )
    # updated_post = cur.fetchone()
    # conn.commit()
    updated_query = db.query(models.Post).filter(models.Post.id == id)
    updated_post = updated_query.first()
    if updated_post is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Post with id: {id} was not found",
        )
    
    updated_query.update(post.model_dump())
    db.commit()
    db.refresh(updated_post)
    return {"data": updated_post} 