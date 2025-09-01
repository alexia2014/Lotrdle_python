import csv
from sqlalchemy import create_engine, MetaData
from sqlalchemy.orm import sessionmaker, Session
from models import Base, Lieu, Personnage, Script

DATABASE_URL = "postgresql://alexpetit:root@localhost:5432/lotrdle"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)
Base.metadata.create_all(engine)

def inserer_donnees_csv_map():
    session = SessionLocal()
    with open("lieux.csv", newline='') as csvfile:
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

def inserer_donnees_csv_pers():
    session = SessionLocal()
    with open("personnes.csv", newline='', encoding="utf-8-sig") as csvfile:
        reader = csv.DictReader(csvfile, delimiter=';')
        for row in reader:
            pers = Personnage(
                name=row['name'],
                birth = row['birth'],
                death = row['death'],
                gender = row['gender'],
                race = row['race'],
                spouse = row['spouse']
            )
            session.add(pers)
        session.commit()
    session.close()

def inserer_donnees_csv_script():
    session = SessionLocal()
    with open("script.csv", newline='') as csvfile:
        reader = csv.DictReader(csvfile, delimiter=';')
        for row in reader:
            pers = Script(
                name=row['name'],
                verse = row['verse'],
                movie = row['movie'],
            )
            session.add(pers)
        session.commit()
    session.close()

def delete_all_base(engine):
    meta = MetaData()
    meta.reflect(bind=engine)
    meta.drop_all(bind=engine)

delete_all_base(engine)
Base.metadata.create_all(bind=engine)
inserer_donnees_csv_map()
inserer_donnees_csv_pers()
inserer_donnees_csv_script()
print("Les données ont été insérées dans la base PostgreSQL.")