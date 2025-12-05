from flask import Blueprint, render_template, request
from models.db import get_db

bp = Blueprint("public", __name__)

@bp.route("/")
def index():
    q = request.args.get("q", "")
    db = get_db()
    query = """
        SELECT p.*, c.nombre AS categoria_nombre
        FROM productos p
        LEFT JOIN categorias c ON p.categoria_id = c.id
    """
    if q:
        query += " WHERE p.nombre LIKE ? OR c.nombre LIKE ?"
        productos = db.execute(query, (f"%{q}%", f"%{q}%")).fetchall()
    else:
        query += " ORDER BY p.id DESC"
        productos = db.execute(query).fetchall()
    return render_template("index.html", productos=productos, q=q)

@bp.route("/categorias")
def categorias():
    q = request.args.get("q", "")
    db = get_db()
    query = "SELECT * FROM categorias"
    if q:
        query += " WHERE nombre LIKE ?"
        categorias = db.execute(query, (f"%{q}%",)).fetchall()
    else:
        query += " ORDER BY nombre"
        categorias = db.execute(query).fetchall()
    return render_template("categorias.html", categorias=categorias, q=q)

@bp.route("/ayuda")
def ayuda():
    return render_template("ayuda.html")

@bp.route("/arriendos")
def arriendos():
    return render_template("arriendos.html")
