from flask import Blueprint, session, request, jsonify, render_template
from models.db import get_db
from utils.decorators import login_required

bp = Blueprint("carrito", __name__)

@bp.route("/carrito")
@login_required
def carrito():
    return render_template("carrito.html")

@bp.route("/confirmar_compra", methods=["POST"])
@login_required
def confirmar_compra():
    import json
    db = get_db()
    data = request.get_json()
    user_email = session["user_email"]
    db.execute("""
        CREATE TABLE IF NOT EXISTS pedidos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_email TEXT,
            producto_id INTEGER,
            nombre TEXT,
            precio REAL,
            cantidad INTEGER,
            subtotal REAL,
            fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    for item in data:
        db.execute(
            "INSERT INTO pedidos (user_email, producto_id, nombre, precio, cantidad, subtotal) VALUES (?, ?, ?, ?, ?, ?)",
            (user_email, item.get("id"), item.get("name"), item.get("price"), item.get("quantity"), item.get("price")*item.get("quantity"))
        )
    db.commit()
    return jsonify({"success": True})
