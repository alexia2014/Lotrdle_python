import csv
from typing import List
from sqlalchemy import create_engine, inspect, text, MetaData
from sqlalchemy.orm import sessionmaker, Session
from models import Base, Lieu
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

def inserer_donnees_csv(fichier_csv):
    session = SessionLocal()
    with open(fichier_csv, newline='') as csvfile:
        reader = csv.DictReader(csvfile, delimiter=';')
        for row in reader:
            lieu = Lieu(
                name=row['name'],
                type=row['Type'],
                mer_proche=[x.strip() for x in row['mer proche'].split(',')] if (row['mer proche'] or row['mer proche'] != "None")  else [],
                capitale=[x.strip() for x in row['capitale'].split(',')] if row['capitale'] else [],
                montagne=[x.strip() for x in row['montagne'].split(',')] if (row['montagne']  or row['mer montagne'] != "None") else [],
                riviere=[x.strip() for x in row['rivière'].split(',')] if row['rivière'] else [],
                bataille=[x.strip() for x in row['bataille'].split(',')] if row['bataille'] else [],
                peuple=[x.strip() for x in row['Peuple'].split(',')] if row['Peuple'] else []
            )
            session.add(lieu)
        session.commit()
    session.close()

def delete_all_base(engine):
    meta = MetaData()
    meta.reflect(bind=engine)
    meta.drop_all(bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
#delete_all_base(engine)
#Base.metadata.create_all(bind=engine)
#inserer_donnees_csv("lieux.csv")
#print("Les données ont été insérées dans la base PostgreSQL.")



@app.get("/")
def test_posts(db: Session = Depends(get_db)):
    fp = open("page_carte.html")
    html_content = fp.read()
    return HTMLResponse(content=html_content, status_code=200)

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