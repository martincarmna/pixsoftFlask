from flask import Flask, render_template, request, redirect, url_for, session, g
import sqlite3
import os

app = Flask(__name__)
app.secret_key = "supersecreto123"
DATABASE = os.path.join(app.root_path, "database.db")

# --------------------------
# Base de datos
# --------------------------
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
    with app.open_resource("schema.sql", mode="r") as f:
        db.executescript(f.read())
    db.commit()

# --------------------------
# Rutas principales
# --------------------------
@app.route("/")
def index():
    db = get_db()
    # Consulta modificada para el index, aunque aquí solo traes productos,
    # es útil traer la categoría también si la plantilla la necesita.
    productos = db.execute("SELECT p.*, c.nombre AS nombre_categoria FROM productos p JOIN categorias c ON p.categoria_id = c.id").fetchall()
    return render_template("index.html", productos=productos)

@app.route('/ayuda')
def ayuda():
    return render_template('ayuda.html')

@app.route('/categorias')
def categorias():
    return render_template('categorias.html')

@app.route('/pedidos')
def pedidos():
    return render_template('pedidos.html')

# --------------------------
# Login
# --------------------------
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
            # Redirigir según tipo de usuario
            if user["email"] == "admin@pixsoft.com":
                return redirect(url_for("admin_productos"))
            else:
                return redirect(url_for("index"))
        else:
            error = "Usuario o contraseña incorrectos"
    return render_template("loginuser.html", error=error)

# --------------------------
# Registro
# --------------------------
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

# --------------------------
# CRUD Productos (solo admin)
# --------------------------
def admin_required(func):
    """Decorador para rutas de admin"""
    def wrapper(*args, **kwargs):
        if session.get("user_email") != "admin@pixsoft.com":
            return "No tienes permisos para acceder a esta página", 403
        return func(*args, **kwargs)
    wrapper.__name__ = func.__name__
    return wrapper

@app.route("/admin/productos")
@admin_required
def admin_productos():
    db = get_db()
    
    # ----------------------------------------------------------------------
    # MODIFICACIÓN CLAVE: Usamos JOIN para obtener el nombre de la categoría
    # y lo asignamos al alias 'nombre_categoria'.
    # ----------------------------------------------------------------------
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
    db = get_db()
    
    # También necesitamos las categorías para el formulario de adición
    categorias = db.execute("SELECT id, nombre FROM categorias ORDER BY nombre").fetchall()
    
    if request.method == "POST":
        nombre = request.form["nombre"]
        precio = request.form["precio"]
        img = request.form["img"]
        categoria_id = request.form["categoria_id"] # Nuevo campo
        
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
    db = get_db()
    db.execute("DELETE FROM productos WHERE id=?", (id,))
    db.commit()
    return redirect(url_for("admin_productos"))

# --------------------------
# Inicialización
# --------------------------
if __name__ == "__main__":
    with app.app_context():
        init_db()

    # Solo llama a app.run una vez
    app.run(debug=True, port=5000)