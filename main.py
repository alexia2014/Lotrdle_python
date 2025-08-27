import csv
from typing import List
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from models import Base, Lieu
from typing import Union
import models
from fastapi import FastAPI, Depends, HTTPException
from pydantic import BaseModel
from fastapi.responses import HTMLResponse
from starlette import status
import lortdle


DATABASE_URL = "postgresql://alexpetit:root@localhost:5432/lotrdle"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)
app = FastAPI()
Base.metadata.create_all(engine)

class Item(BaseModel):
    name: str
    price: float
    is_offer: Union[bool, None] = None

def inserer_donnees_csv(fichier_csv):
    session = SessionLocal()
    with open(fichier_csv, newline='') as csvfile:
        reader = csv.DictReader(csvfile, delimiter=';')
        for row in reader:
            lieu = Lieu(
                name=row['name'],
                type=row['Type'],
                mer_proche=[x.strip() for x in row['mer proche'].split(',')] if row['mer proche'] else [],
                capitale=row['capitale'],
                montagne=[x.strip() for x in row['montagne'].split(',')] if row['montagne'] else [],
                riviere=row['rivière'] if row['rivière'] != 'None' else None,
                bataille=[x.strip() for x in row['bataille'].split(',')] if row['bataille'] else [],
                peuple=[x.strip() for x in row['Peuple'].split(',')] if row['Peuple'] else []
            )
            session.add(lieu)
        session.commit()
    session.close()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
#inserer_donnees_csv("lieux.csv")
#print("Les données ont été insérées dans la base PostgreSQL.")



@app.get("/")
def test_posts(db: Session = Depends(get_db)):
    post = db.query(models.Lieu).all()
    return post

@app.get("/{name}", status_code=status.HTTP_200_OK)
def get_test_one(name: str, db: Session = Depends(get_db)):
    id_guest = db.query(models.Lieu).filter(models.Lieu.name == name).first()
    if id_guest is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"The id: {name} you requested for does not exist")
    return id_guest