import csv
from sqlalchemy import create_engine, MetaData
from sqlalchemy.orm import sessionmaker, Session
from models import Base, Lieu, Personnage, Script
import sys
from lortdle import compare_date

def inserer_donnees_csv_map(session):
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

def inserer_donnees_csv_pers(session):
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

def inserer_donnees_csv_script(session):
    with open("script_clean.csv", newline='') as csvfile:
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

def check_date_personne():
    with open("personnes.csv", newline='', encoding="utf-8-sig") as csvfile:
        reader = csv.DictReader(csvfile, delimiter=';')
        for row in reader:
            birth = compare_date(row['birth'])
            death = compare_date(row['death'])
            if (birth != 0 and death != 0 and birth >= death):
                print("ERROR: " + row['name'] + ": " + str(birth) + " to " + str(death))

def check_personne():
    races = ["Men", "Hobbit", "Elf", "Dwarf", "Orc", "Uruk-hai", "Dragon", "Ainur", "Maiar", "Nazgûl", "God", "Half-elven", "Eagle", "Balrog", "Skin-changer", "Spider", "Ent", "Stone-trolls", "Werewolf"]
    with open("personnes.csv", newline='', encoding="utf-8-sig") as csvfile:
        reader = csv.DictReader(csvfile, delimiter=';')
        for row in reader:
            race = row['race']
            if (race not in races):
                print("ERROR: " + row['name'] + ": " + race)

def delete_all_base(engine):
    meta = MetaData()
    meta.reflect(bind=engine)
    meta.drop_all(bind=engine)

def main():
    args = sys.argv[1:]
    DATABASE_URL = "postgresql://"+ args[0] + ":" + args[1] +"@localhost:5432/" + args[2]
    engine = create_engine(DATABASE_URL)
    SessionLocal = sessionmaker(bind=engine)
    Base.metadata.create_all(engine)
    delete_all_base(engine)
    Base.metadata.create_all(bind=engine)
    session = SessionLocal()
    check_date_personne()
    check_personne()
    inserer_donnees_csv_map(session)
    inserer_donnees_csv_pers(session)
    inserer_donnees_csv_script(session)
    print("Les données ont été insérées dans la base PostgreSQL.")

main()