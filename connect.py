import psycopg2
from psycopg2 import sql

# Connexion en tant que superutilisateur PostgreSQL (ex: 'postgres')
conn = psycopg2.connect(dbname="postgres", user="postgres", password="root", host="localhost", port="5432")
conn.autocommit = True
cur = conn.cursor()

# Création de l'utilisateur
try:
    cur.execute("CREATE USER alexpetit WITH PASSWORD 'root';")
    print("Utilisateur 'alexpetit' créé.")
except psycopg2.errors.DuplicateObject:
    print("Utilisateur 'alexpetit' existe déjà.")

# Création de la base
try:
    cur.execute("CREATE DATABASE lotrdle OWNER alexpetit;")
    print("Base 'lotrdle' créée.")
except psycopg2.errors.DuplicateDatabase:
    print("Base 'lotrdle' existe déjà.")

# Test de connexion avec le nouvel utilisateur
try:
    test_conn = psycopg2.connect(
        dbname="lotrdle",
        user="alexpetit",
        password="root",
        host="localhost",
        options='-c client_encoding=UTF8'
    )
    print("Connexion réussie avec l'utilisateur 'alexpetit'.")
    test_conn.close()
except Exception as e:
    print("Échec de la connexion :", repr(e))

cur.close()
conn.close()
