from flask import Blueprint, render_template, request, redirect, url_for
from werkzeug.utils import secure_filename
from models.db import get_db
from utils.decorators import admin_required
import os
from config import Config

bp = Blueprint("admin", __name__, url_prefix="/admin")

@bp.route("/productos")
@admin_required
def admin_productos():
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
    return render_template("admin_productos.html", productos=productos, q=q)

@bp.route("/productos/add", methods=["GET", "POST"])
@admin_required
def add_producto():
    db = get_db()
    categorias = db.execute("SELECT id, nombre FROM categorias ORDER BY nombre").fetchall()
    if request.method == "POST":
        nombre = request.form.get("nombre")
        precio = request.form.get("precio")
        categoria_id = request.form.get("categoria")
        archivo = request.files.get("img")
        if archivo and archivo.filename != "":
            nombre_archivo = secure_filename(archivo.filename)
            archivo.save(os.path.join(Config.UPLOAD_FOLDER, nombre_archivo))
        else:
            nombre_archivo = None
        db.execute(
            "INSERT INTO productos (nombre, precio, img, categoria_id) VALUES (?, ?, ?, ?)",
            (nombre, precio, nombre_archivo, categoria_id)
        )
        db.commit()
        return redirect(url_for("admin.admin_productos"))
    return render_template("add_producto.html", categorias=categorias)

@bp.route("/productos/edit/<int:id>", methods=["GET", "POST"])
@admin_required
def edit_producto(id):
    db = get_db()
    categorias = db.execute("SELECT id, nombre FROM categorias ORDER BY nombre").fetchall()
    producto = db.execute("SELECT * FROM productos WHERE id=?", (id,)).fetchone()
    if not producto:
        return "Producto no encontrado", 404
    error = None
    if request.method == "POST":
        nombre = request.form.get("nombre")
        precio = request.form.get("precio")
        categoria_id = request.form.get("categoria")
        img_file = request.files.get("img")
        if img_file and img_file.filename != "":
            img = secure_filename(img_file.filename)
            img_file.save(os.path.join(Config.UPLOAD_FOLDER, img))
        else:
            img = producto["img"]
        if not nombre or not precio or not categoria_id:
            error = "Completa todos los campos"
        else:
            db.execute(
                "UPDATE productos SET nombre=?, precio=?, img=?, categoria_id=? WHERE id=?",
                (nombre, precio, img, categoria_id, id)
            )
            db.commit()
            return redirect(url_for("admin.admin_productos"))
    return render_template("edit_producto.html", producto=producto, categorias=categorias, error=error)

@bp.route("/productos/delete/<int:id>")
@admin_required
def delete_producto(id):
    db = get_db()
    db.execute("DELETE FROM productos WHERE id=?", (id,))
    db.commit()
    return redirect(url_for("admin.admin_productos"))
