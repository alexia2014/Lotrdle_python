import csv
from typing import List
from sqlalchemy import create_engine, inspect, text, MetaData
from sqlalchemy.orm import sessionmaker, Session
from models import Base, Lieu, Personnage
from typing import Union
import models
from fastapi import FastAPI, Depends, HTTPException
from pydantic import BaseModel
from fastapi.responses import HTMLResponse
from starlette import status
import lortdle
import json

DATABASE_URL = "postgresql://alexpetit:root@localhost:5432/lotrdle"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)
app = FastAPI()
Base.metadata.create_all(engine)
answer = None

class Item(BaseModel):
    name: str


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/")
def test_posts(db: Session = Depends(get_db)):
    fp = open("page_principal.html")
    html_content = fp.read()
    return HTMLResponse(content=html_content, status_code=200)

@app.get("/classic")
def test_posts(db: Session = Depends(get_db)):
    fp = open("page.html")
    html_content = fp.read()
    return HTMLResponse(content=html_content, status_code=200)

@app.get("/carte")
def test_posts(db: Session = Depends(get_db)):
    fp = open("page_carte.html")
    html_content = fp.read()
    return HTMLResponse(content=html_content, status_code=200)

@app.post("/classic/initTable", status_code=status.HTTP_200_OK)
def get_test_one(db: Session = Depends(get_db)):
    inspector = inspect(db.bind)
    table_names = inspector.get_table_names()
    result = {}
    columns = inspector.get_columns('personnes')
    column_names = [col["name"] for col in columns]
    result['personnes'] = column_names
    columns = [col["name"] for col in inspector.get_columns('personnes')]
    if "name" in columns:
        query = text(f"SELECT DISTINCT name FROM {'personnes'}")
        rows = db.execute(query).fetchall()
        result["name"] = [row[0] for row in rows]
    nb = len(result["name"])
    answer_index = lortdle.init(nb)
    global answer
    answer = db.query(Personnage).filter(Personnage.id == answer_index).first()
    print(answer.name)
    if result is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"The id: {result} you requested for does not exist")
    return result

@app.post("/classic/checkGuess", status_code=status.HTTP_200_OK)
def get_test_one(item: Item, db: Session = Depends(get_db)):
    if item.name and item.name[0] == "\"":
        item.name = item.name[1:]
    if item.name == "":
        result = {"columns": [],"found": 0}
        return result
    inspector = inspect(db.bind)
    pers = db.query(Personnage).filter(Personnage.name.ilike(item.name)).first()
    global answer
    columns = inspector.get_columns('personnes')
    column_names = [col["name"] for col in columns]
    guess_an = lortdle.check_guess(pers, answer, column_names)
    return guess_an

@app.post("/carte/initTable", status_code=status.HTTP_200_OK)
def get_test_one(db: Session = Depends(get_db)):
    inspector = inspect(db.bind)
    table_names = inspector.get_table_names()
    result = {}
    columns = inspector.get_columns('lieux')
    column_names = [col["name"] for col in columns]
    result['lieux'] = column_names
    columns = [col["name"] for col in inspector.get_columns('lieux')]
    if "name" in columns:
        query = text(f"SELECT DISTINCT name FROM {'lieux'}")
        rows = db.execute(query).fetchall()
        result["name"] = [row[0] for row in rows]
    nb = len(result["name"])
    answer_index = lortdle.init(nb)
    global answer
    answer = db.query(Lieu).filter(Lieu.id == answer_index).first()
    print(answer.name)
    if result is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"The id: {result} you requested for does not exist")
    return result

@app.post("/carte/checkGuess", status_code=status.HTTP_200_OK)
def get_test_one(item: Item, db: Session = Depends(get_db)):
    if item.name == "":
        result = {"columns": [],"found": 0}
        return result
    inspector = inspect(db.bind)
    lieu = db.query(Lieu).filter(Lieu.name.ilike(item.name)).first()
    global answer
    columns = inspector.get_columns('lieux')
    column_names = [col["name"] for col in columns]
    guess_an = lortdle.check_guess(lieu, answer, column_names)
    return guess_an