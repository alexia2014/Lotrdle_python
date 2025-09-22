import csv
from typing import List
from sqlalchemy import create_engine, inspect, text, MetaData
from sqlalchemy.orm import sessionmaker, Session
from models import Base, Lieu, Personnage, Script
from typing import Union
import models
from fastapi import FastAPI, Depends, HTTPException
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from starlette import status
import lortdle
import httpx
import json

DATABASE_URL = "postgresql://alexpetit:root@localhost:5432/lotrdle"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)
app = FastAPI()


app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8000", "http://127.0.0.1:8000"],  # adapte selon ton port
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

Base.metadata.create_all(engine)
app.mount('/static', StaticFiles(directory='static', html=True), name='static')

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
    fp = open("static/page_principal.html")
    html_content = fp.read()
    return HTMLResponse(content=html_content, status_code=200)

@app.get("/classic")
def test_posts(db: Session = Depends(get_db)):
    fp = open("static/page_classic.html")
    html_content = fp.read()
    return HTMLResponse(content=html_content, status_code=200)

@app.get("/carte")
def test_posts(db: Session = Depends(get_db)):
    fp = open("static/page_carte.html")
    html_content = fp.read()
    return HTMLResponse(content=html_content, status_code=200)

@app.post("/classic/initTable", status_code=status.HTTP_200_OK)
def get_test_one(db: Session = Depends(get_db)):
    answer, result = get_answer(db, "personnes")
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
    answer, _ = get_answer(db, "personnes")
    columns = inspector.get_columns('personnes')
    column_names = [col["name"] for col in columns]
    guess_an = lortdle.check_guess(pers, answer, column_names)
    return guess_an

@app.post("/carte/initTable", status_code=status.HTTP_200_OK)
def get_test_one(db: Session = Depends(get_db)):
    answer, result = get_answer(db, "lieux")
    if result is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"The id: {result} you requested for does not exist")
    return result

@app.post("/carte/checkGuess", status_code=status.HTTP_200_OK)
def get_test_one(item: Item, db: Session = Depends(get_db)):
    if item.name and item.name[0] == "\"":
        item.name = item.name[1:]
    if item.name == "":
        result = {"columns": [],"found": 0}
        return result
    inspector = inspect(db.bind)
    lieu = db.query(Lieu).filter(Lieu.name.ilike(item.name)).first()
    answer, _ = get_answer(db, "lieux")
    columns = inspector.get_columns('lieux')
    column_names = [col["name"] for col in columns]
    guess_an = lortdle.check_guess(lieu, answer, column_names)
    return guess_an

@app.get("/script")
def test_posts(db: Session = Depends(get_db)):
    fp = open("static/page_script.html")
    html_content = fp.read()
    return HTMLResponse(content=html_content, status_code=200)

@app.post("/script/initTable", status_code=status.HTTP_200_OK)
def get_test_one(db: Session = Depends(get_db)):
    answer, result = get_answer(db, "scripting")
    result["verse"] = "\"" + answer.verse + "\""
    result["movie"] = answer.movie
    if result is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"The id: {result} you requested for does not exist")
    return result

@app.post("/script/checkGuess", status_code=status.HTTP_200_OK)
def get_test_one(item: Item, db: Session = Depends(get_db)):
    if item.name and item.name[0] == "\"":
        item.name = item.name[1:]
    if item.name == "":
        result = {"columns": [],"found": 0}
        return result
    inspector = inspect(db.bind)
    lieu = db.query(Script).filter(Script.name.ilike(item.name)).first()
    answer, _ = get_answer(db, "scripting")
    if lieu:
        if (getattr(lieu, "name") == getattr(answer, "name")):
            result = {"columns": ["<span style=\"color:green;\">"+ item.name +"</span>"], "found": 1, "verse": getattr(answer, "verse"), "movie": getattr(answer, "movie"), "color": ["green"]}
        else:
            result = {"columns": ["<span style=\"color:red;\">"+ item.name +"</span>"], "found": 0, "color": ["red"]}
    else:
        result = {"columns": [],"found": 0}
    return result

def get_answer(db, name):
    inspector = inspect(db.bind)
    table_names = inspector.get_table_names()
    result = {}
    columns = inspector.get_columns(name)
    column_names = [col["name"] for col in columns]
    result['lieux'] = column_names
    columns = [col["name"] for col in inspector.get_columns(name)]
    if "name" in columns:
        query = text(f"SELECT DISTINCT name FROM " + name)
        rows = db.execute(query).fetchall()
        result["name"] = [row[0] for row in rows]
    nb = len(result["name"])
    answer_index = lortdle.init(nb)
    if name == "scripting":
        name = Script
    elif name == "lieux":
        name = Lieu
    elif name == "personnes":
        name = Personnage
    return db.query(name).filter(name.id == answer_index).first(), result


@app.get("/youtube-search")
async def youtube_search(q: str):
    YOUTUBE_API_KEY = "AIzaSyBCSRWtfbrLnRw1ZTd1R1oELHQsUyLrVds"
    url = (
        "https://www.googleapis.com/youtube/v3/search"
        f"?part=snippet&q={q}&type=video&maxResults=1&key={YOUTUBE_API_KEY}"
    )
    async with httpx.AsyncClient() as client:
        response = await client.get(url)
        data = response.json()
        if "items" in data and data["items"]:
            video_id = data["items"][0]["id"]["videoId"]
            return {"videoId": video_id}
        return {"error": "Aucune vidéo trouvée"}