import sqlite3
import os
from flask import Flask, render_template, request, redirect, url_for, session, g

# ============================================================
# 1. CONFIGURACIÓN DE LA APLICACIÓN
# ============================================================
app = Flask(__name__)
app.secret_key = "supersecreto123"  # Cambia en producción
DATABASE = os.path.join(app.root_path, "database.db")

# ============================================================
# 2. BASE DE DATOS (SQLite)
# ============================================================
def get_db():
    db = getattr(g, "_database", None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
        db.row_factory = sqlite3.Row
    return db

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, "_database", None)
    if db is not None:
        db.close()

def init_db():
    db = get_db()
    try:
        with app.open_resource("schema.sql", mode="r", encoding="utf-8") as f:
            db.executescript(f.read())
        db.commit()
    except FileNotFoundError:
        print("ADVERTENCIA: No se encontró 'schema.sql'. La base de datos no se inicializó.")

# ============================================================
# 3. DECORADOR ADMIN
# ============================================================
def admin_required(func):
    def wrapper(*args, **kwargs):
        if session.get("user_email") != "admin@pixsoft.com":
            return "No tienes permisos para acceder a esta página", 403
        return func(*args, **kwargs)
    wrapper.__name__ = func.__name__
    return wrapper

# ============================================================
# 4. RUTAS PÚBLICAS
# ============================================================
@app.route("/")
def index():
    db = get_db()
    productos = db.execute("""
        SELECT p.*, c.nombre AS categoria_nombre
        FROM productos p
        LEFT JOIN categorias c ON p.categoria_id = c.id
        ORDER BY p.id DESC
    """).fetchall()
    return render_template("index.html", productos=productos)

@app.route("/ayuda")
def ayuda():
    return render_template("ayuda.html")

@app.route("/categorias")
def categorias():
    db = get_db()
    # Obtener todas las categorías
    categorias = db.execute("SELECT id, nombre FROM categorias ORDER BY nombre").fetchall()
    
    # Crear un diccionario con productos por categoría
    productos_por_categoria = {}
    for cat in categorias:
        productos = db.execute(
            "SELECT * FROM productos WHERE categoria_id=? ORDER BY id DESC", (cat["id"],)
        ).fetchall()
        productos_por_categoria[cat["nombre"]] = productos

    return render_template("categorias.html",
                           categorias=categorias,
                           productos_por_categoria=productos_por_categoria)



@app.route("/pedidos")
def pedidos():
    return render_template("pedidos.html")

@app.route("/arriendos")
def arriendos():
    return render_template("arriendos.html")

# ============================================================
# 5. LOGIN Y REGISTRO
# ============================================================
@app.route("/loginuser", methods=["GET", "POST"])
def loginuser():
    error = None
    if request.method == "POST":
        email = request.form["username"]
        password = request.form["password"]
        db = get_db()
        user = db.execute(
            "SELECT * FROM usuarios WHERE email=? AND password=?",
            (email, password)
        ).fetchone()
        if user:
            session["user"] = user["nombre"]
            session["user_email"] = user["email"]
            if user["email"] == "admin@pixsoft.com":
                return redirect(url_for("admin_productos"))
            return redirect(url_for("index"))
        else:
            error = "Usuario o contraseña incorrectos"
    return render_template("loginuser.html", error=error)

@app.route("/register", methods=["GET", "POST"])
def register_user():
    error = None
    if request.method == "POST":
        nombre = request.form["nombre"]
        email = request.form["email"]
        password = request.form["password"]
        confirm_password = request.form["confirm_password"]
        if password != confirm_password:
            error = "Las contraseñas no coinciden"
        else:
            db = get_db()
            try:
                db.execute(
                    "INSERT INTO usuarios (nombre, email, password) VALUES (?, ?, ?)",
                    (nombre, email, password)
                )
                db.commit()
                session["user"] = nombre
                session["user_email"] = email
                return redirect(url_for("index"))
            except sqlite3.IntegrityError:
                error = "El correo ya está registrado"
    return render_template("register.html", error=error)

@app.route("/logout")
def logout():
    session.pop("user", None)
    session.pop("user_email", None)
    return redirect(url_for("index"))

# ============================================================
# 6. CRUD PRODUCTOS (ADMIN)
# ============================================================
@app.route("/admin/productos")
@admin_required
def admin_productos():
    db = get_db()
    productos = db.execute("""
        SELECT p.*, c.nombre AS categoria_nombre
        FROM productos p
        LEFT JOIN categorias c ON p.categoria_id = c.id
        ORDER BY p.id DESC
    """).fetchall()
    return render_template("admin_productos.html", productos=productos)

@app.route("/admin/productos/add", methods=["GET", "POST"])
@admin_required
def add_producto():
    db = get_db()
    categorias = db.execute("SELECT id, nombre FROM categorias ORDER BY nombre").fetchall()
    error = None
    if request.method == "POST":
        nombre = request.form.get("nombre", "").strip()
        precio = request.form.get("precio", "").strip()
        img = request.form.get("img", "").strip()
        categoria_id = request.form.get("categoria", "").strip()

        if not nombre or not precio or not categoria_id:
            error = "Por favor completa todos los campos obligatorios"
        else:
            try:
                precio_float = float(precio)
                db.execute(
                    "INSERT INTO productos (nombre, precio, img, categoria_id) VALUES (?, ?, ?, ?)",
                    (nombre, precio_float, img, categoria_id)
                )
                db.commit()
                return redirect(url_for("admin_productos"))
            except ValueError:
                error = "El precio debe ser un número válido"

    return render_template("add_producto.html", categorias=categorias, error=error)

@app.route("/admin/productos/edit/<int:id>", methods=["GET", "POST"])
@admin_required
def edit_producto(id):
    db = get_db()
    categorias = db.execute("SELECT id, nombre FROM categorias ORDER BY nombre").fetchall()
    producto = db.execute("SELECT * FROM productos WHERE id=?", (id,)).fetchone()
    error = None

    if request.method == "POST":
        nombre = request.form.get("nombre", "").strip()
        precio = request.form.get("precio", "").strip()
        img = request.form.get("img", "").strip()
        categoria_id = request.form.get("categoria", "").strip()

        if not nombre or not precio or not categoria_id:
            error = "Por favor completa todos los campos obligatorios"
        else:
            try:
                precio_float = float(precio)
                db.execute(
                    "UPDATE productos SET nombre=?, precio=?, img=?, categoria_id=? WHERE id=?",
                    (nombre, precio_float, img, categoria_id, id)
                )
                db.commit()
                return redirect(url_for("admin_productos"))
            except ValueError:
                error = "El precio debe ser un número válido"

    return render_template("edit_producto.html", producto=producto, categorias=categorias, error=error)

@app.route("/admin/productos/delete/<int:id>")
@admin_required
def delete_producto(id):
    db = get_db()
    db.execute("DELETE FROM productos WHERE id=?", (id,))
    db.commit()
    return redirect(url_for("admin_productos"))

# ============================================================
# 7. RUTAS DEL CARRITO
# ============================================================
@app.route("/carrito")
def carrito():
    return render_template("carrito.html")

@app.route("/confirmar_compra", methods=["POST"])
def confirmar_compra():
    import json
    if not session.get("user_email"):
        return {"success": False, "error": "Debes iniciar sesión"}, 401

    try:
        data = request.get_json()
        if not data:
            return {"success": False, "error": "Carrito vacío"}

        db = get_db()
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
        db.commit()

        for item in data:
            db.execute(
                "INSERT INTO pedidos (user_email, producto_id, nombre, precio, cantidad, subtotal) VALUES (?, ?, ?, ?, ?, ?)",
                (user_email, item.get("id"), item.get("name"), item.get("price"), item.get("quantity"), item.get("price") * item.get("quantity"))
            )
        db.commit()

        return {"success": True}
    except Exception as e:
        print("Error al confirmar compra:", e)
        return {"success": False, "error": str(e)}
    
@app.route("/buscar", methods=["GET"])
def buscar():
    query = request.args.get("q", "").strip()
    db = get_db()
    if query:
        # Busca productos por nombre o por categoría
        productos = db.execute("""
            SELECT p.*, c.nombre AS categoria_nombre
            FROM productos p
            LEFT JOIN categorias c ON p.categoria_id = c.id
            WHERE p.nombre LIKE ? OR c.nombre LIKE ?
            ORDER BY p.id DESC
        """, (f"%{query}%", f"%{query}%")).fetchall()
    else:
        # Si no hay query, mostrar todos
        productos = db.execute("""
            SELECT p.*, c.nombre AS categoria_nombre
            FROM productos p
            LEFT JOIN categorias c ON p.categoria_id = c.id
            ORDER BY p.id DESC
        """).fetchall()

    return render_template("index.html", productos=productos, query=query)

# ============================================================
# 8. INICIALIZACIÓN
# ============================================================
if __name__ == "__main__":
    with app.app_context():
        init_db()
    app.run(debug=True, port=5000)
