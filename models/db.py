import sqlite3
from flask import g
from config import Config

def get_db():
    db = getattr(g, "_database", None)
    if db is None:
        db = g._database = sqlite3.connect(Config.DATABASE)
        db.row_factory = sqlite3.Row
    return db

def close_db(e=None):
    db = getattr(g, "_database", None)
    if db is not None:
        db.close()

def init_db(app):
    db = get_db()
    try:
        with app.open_resource("schema.sql", mode="r", encoding="utf-8") as f:
            db.executescript(f.read())
        db.commit()
    except FileNotFoundError:
        print("No se encontró 'schema.sql'. Base de datos no inicializada.")
