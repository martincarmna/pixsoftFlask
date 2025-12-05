import sqlite3
import os
from flask import Flask, render_template, request, redirect, url_for, session, g

# ============================================================
#  1. CONFIGURACIÓN DE LA APLICACIÓN
# ============================================================
app = Flask(__name__)
# ¡IMPORTANTE! Usar una clave secreta fuerte en producción.
app.secret_key = "supersecreto123" 
# Ruta al archivo de la base de datos SQLite
DATABASE = os.path.join(app.root_path, "database.db")


# ============================================================
#  2. GESTIÓN DE LA BASE DE DATOS (SQLite)
# ============================================================
def get_db():
    """Establece la conexión a la base de datos y la almacena en 'g'."""
    db = getattr(g, "_database", None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
        # Permite acceder a las filas como diccionarios (por nombre de columna)
        db.row_factory = sqlite3.Row
    return db


@app.teardown_appcontext
def close_connection(exception):
    """Cierra la conexión a la base de datos al finalizar el contexto de la aplicación."""
    db = getattr(g, "_database", None)
    if db is not None:
        db.close()


def init_db():
    """Inicializa la base de datos usando el esquema definido en 'schema.sql'."""
    db = get_db()
    try:
        with app.open_resource("schema.sql", mode="r") as f:
            db.executescript(f.read())
        db.commit()
    except FileNotFoundError:
        print("ADVERTENCIA: No se encontró 'schema.sql'. La base de datos no se inicializó.")


# ============================================================
#  3. DECORADOR Y UTILERÍAS
# ============================================================
def admin_required(func):
    """Decorador para restringir el acceso solo al usuario administrador."""
    def wrapper(*args, **kwargs):
        if session.get("user_email") != "admin@pixsoft.com":
            # Devolver un error 403 (Prohibido) si no es el administrador
            return "No tienes permisos para acceder a esta página", 403
        return func(*args, **kwargs)
    wrapper.__name__ = func.__name__ # Necesario para Flask
    return wrapper


# ============================================================
#  4. RUTAS PRINCIPALES (PÚBLICAS)
# ============================================================
@app.route("/")
def index():
    """Página de inicio que muestra todos los productos con sus categorías."""
    db = get_db()
    # Consulta que une productos y categorías para mostrar información completa
    productos = db.execute("""
        SELECT 
            p.*, 
            c.nombre AS nombre_categoria 
        FROM 
            productos p 
        JOIN 
            categorias c ON p.categoria_id = c.id
        ORDER BY 
            p.id DESC
    """).fetchall()
    return render_template("index.html", productos=productos)


@app.route('/ayuda')
def ayuda():
    """Página de Ayuda."""
    return render_template('ayuda.html')


@app.route('/categorias')
def categorias():
    """Página de Categorías (Placeholder)."""
    return render_template('categorias.html')


@app.route('/pedidos')
def pedidos():
    """Página de Pedidos (Placeholder)."""
    return render_template('pedidos.html')


@app.route("/arriendos")
def arriendos():
    """Página de Arriendos (Placeholder)."""
    return render_template("arriendos.html")


# ============================================================
#  5. LOGIN Y REGISTRO
# ============================================================
@app.route("/loginuser", methods=["GET", "POST"])
def loginuser():
    """Maneja el inicio de sesión de usuarios."""
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

            # Redirigir según tipo de usuario
            if user["email"] == "admin@pixsoft.com":
                return redirect(url_for("admin_productos"))
            return redirect(url_for("index"))
        else:
            error = "Usuario o contraseña incorrectos"

    return render_template("loginuser.html", error=error)


@app.route("/register", methods=["GET", "POST"])
def register_user():
    """Maneja el registro de nuevos usuarios."""
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

                # Iniciar sesión automáticamente
                session["user"] = nombre
                session["user_email"] = email

                return redirect(url_for("index"))

            except sqlite3.IntegrityError:
                error = "El correo ya está registrado"

    return render_template("register.html", error=error)


@app.route("/logout")
def logout():
    """Cierra la sesión del usuario."""
    session.pop("user", None)
    session.pop("user_email", None)
    return redirect(url_for("index"))


# ============================================================
#  6. CRUD PRODUCTOS (ADMIN)
# ============================================================
@app.route("/admin/productos")
@admin_required
def admin_productos():
    """Muestra la lista de productos en el panel de administración."""
    db = get_db()
    
    # Usamos JOIN para obtener el nombre de la categoría
    productos = db.execute("""
        SELECT 
            p.*, 
            c.nombre AS nombre_categoria
        FROM 
            productos p
        JOIN 
            categorias c ON p.categoria_id = c.id
        ORDER BY 
            p.id DESC
    """).fetchall()
    
    return render_template("admin_productos.html", productos=productos)


@app.route("/admin/productos/add", methods=["GET", "POST"])
@admin_required
def add_producto():
    """Permite añadir un nuevo producto, requiriendo una categoría."""
    db = get_db()
    
    # Necesitamos todas las categorías para el formulario de selección
    categorias = db.execute("SELECT id, nombre FROM categorias ORDER BY nombre").fetchall()
    
    if request.method == "POST":
        nombre = request.form["nombre"]
        precio = request.form["precio"]
        img = request.form["img"]
        categoria_id = request.form["categoria_id"] # El ID de la categoría seleccionada
        
        db.execute(
            "INSERT INTO productos (nombre, precio, img, categoria_id) VALUES (?, ?, ?, ?)",
            (nombre, precio, img, categoria_id)
        )
        db.commit()
        return redirect(url_for("admin_productos"))
    
    # Pasamos las categorías a la plantilla de adición
    return render_template("add_producto.html", categorias=categorias)


@app.route("/admin/productos/edit/<int:id>", methods=["GET", "POST"])
@admin_required
def edit_producto(id):
    """Permite editar un producto existente, incluyendo su categoría."""
    db = get_db()
    
    # Obtenemos todas las categorías para el select box
    categorias = db.execute("SELECT id, nombre FROM categorias ORDER BY nombre").fetchall()
    
    # Obtenemos el producto actual
    producto = db.execute("SELECT * FROM productos WHERE id=?", (id,)).fetchone()
    
    if request.method == "POST":
        nombre = request.form["nombre"]
        precio = request.form["precio"]
        img = request.form["img"]
        categoria_id = request.form["categoria_id"] # Nuevo campo
        
        db.execute(
            "UPDATE productos SET nombre=?, precio=?, img=?, categoria_id=? WHERE id=?",
            (nombre, precio, img, categoria_id, id)
        )
        db.commit()
        return redirect(url_for("admin_productos"))
    
    return render_template("edit_producto.html", producto=producto, categorias=categorias)


@app.route("/admin/productos/delete/<int:id>")
@admin_required
def delete_producto(id):
    """Elimina un producto por ID."""
    db = get_db()
    db.execute("DELETE FROM productos WHERE id=?", (id,))
    db.commit()
    return redirect(url_for("admin_productos"))


# ============================================================
#  7. INICIALIZACIÓN
# ============================================================
if __name__ == "__main__":
    # Asegura que la DB se inicialice antes de ejecutar la aplicación
    with app.app_context():
        init_db()

    app.run(debug=True, port=5000)