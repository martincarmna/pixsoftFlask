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
    """Conexión a la base de datos almacenada en g"""
    db = getattr(g, "_database", None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
        db.row_factory = sqlite3.Row
    return db

@app.teardown_appcontext
def close_connection(exception):
    """Cierra la conexión al terminar la request"""
    db = getattr(g, "_database", None)
    if db is not None:
        db.close()

def init_db():
    """Inicializa la DB desde schema.sql"""
    db = get_db()
    try:
        # IMPORTANTE: abrir con UTF-8 para evitar errores en Windows
        with app.open_resource("schema.sql", mode="r", encoding="utf-8") as f:
            db.executescript(f.read())
        db.commit()
    except FileNotFoundError:
        print("ADVERTENCIA: No se encontró 'schema.sql'. La base de datos no se inicializó.")

# ============================================================
# 3. DECORADOR ADMIN
# ============================================================
def admin_required(func):
    """Restringe acceso solo a admin"""
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
    """Lista de productos públicos"""
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
    categorias = db.execute("SELECT * FROM categorias ORDER BY nombre").fetchall()
    return render_template("categorias.html", categorias=categorias)

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
    if request.method == "POST":
        nombre = request.form.get("nombre")
        precio = request.form.get("precio")
        img = request.form.get("img")
        categoria_id = request.form.get("categoria")

        if not categoria_id:
            return "Debes seleccionar una categoría", 400

        db.execute(
            "INSERT INTO productos (nombre, precio, img, categoria_id) VALUES (?, ?, ?, ?)",
            (nombre, precio, img, categoria_id)
        )
        db.commit()
        return redirect(url_for("admin_productos"))
    return render_template("add_producto.html", categorias=categorias)

@app.route("/admin/productos/edit/<int:id>", methods=["GET", "POST"])
@admin_required
def edit_producto(id):
    db = get_db()
    categorias = db.execute("SELECT id, nombre FROM categorias ORDER BY nombre").fetchall()
    producto = db.execute("SELECT * FROM productos WHERE id=?", (id,)).fetchone()
    
    if not producto:
        return "Producto no encontrado", 404

    error = None

    if request.method == "POST":
        nombre = request.form.get("nombre", "").strip()
        precio = request.form.get("precio", "").strip()
        img = request.form.get("img", "").strip()
        categoria_id = request.form.get("categoria", "").strip()  # <-- coincide con el HTML

        # Validación
        if not nombre or not precio or not categoria_id:
            error = "Por favor completa todos los campos obligatorios"
        else:
            try:
                precio_float = float(precio.replace(",", "."))
                categoria_id_int = int(categoria_id)
                db.execute(
                    "UPDATE productos SET nombre=?, precio=?, img=?, categoria_id=? WHERE id=?",
                    (nombre, precio_float, img, categoria_id_int, id)
                )
                db.commit()
                return redirect(url_for("admin_productos"))
            except ValueError:
                error = "El precio o categoría no son válidos"
            except sqlite3.Error as e:
                error = f"Error al actualizar: {e}"

    return render_template("edit_producto.html", producto=producto, categorias=categorias, error=error)



@app.route("/admin/productos/delete/<int:id>")
@admin_required
def delete_producto(id):
    db = get_db()
    db.execute("DELETE FROM productos WHERE id=?", (id,))
    db.commit()
    return redirect(url_for("admin_productos"))

# ============================================================
# RUTAS DEL CARRITO
# ============================================================
@app.route("/carrito")
def carrito():
    """Renderiza la página del carrito de compras."""
    return render_template("carrito.html")

@app.route("/confirmar_compra", methods=["POST"])
def confirmar_compra():
    """Recibe el carrito en JSON y lo guarda como pedido en la DB."""
    import json
    if not session.get("user_email"):
        return {"success": False, "error": "Debes iniciar sesión"}, 401

    try:
        data = request.get_json()  # El carrito enviado desde JS
        if not data:
            return {"success": False, "error": "Carrito vacío"}

        db = get_db()
        user_email = session["user_email"]

        # Crear tabla de pedidos si no existe
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

        # Insertar cada producto del carrito
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

# ============================================================
# 7. INICIALIZACIÓN
# ============================================================
if __name__ == "__main__":
    with app.app_context():
        init_db()  # Inicializa DB
    app.run(debug=True, port=5000)
