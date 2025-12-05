from flask import Flask, render_template, request, redirect, url_for, session, g
import sqlite3
import os

app = Flask(__name__)
app.secret_key = "supersecreto123"
DATABASE = os.path.join(app.root_path, "database.db")

# -----------------------------------
# Funciones de base de datos
# -----------------------------------
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

# -----------------------------------
# Rutas principales
# -----------------------------------
@app.route("/")
def index():
    db = get_db()
    productos = db.execute("SELECT * FROM productos").fetchall()
    return render_template("index.html", productos=productos, user=session.get("user"))

@app.route("/loginuser", methods=["GET", "POST"])
def loginuser():
    error = None
    if request.method == "POST":
        email = request.form["username"]
        password = request.form["password"]

        db = get_db()
        user = db.execute("SELECT * FROM usuarios WHERE email=? AND password=?", (email, password)).fetchone()

        if user:
            session["user"] = user["nombre"]
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
                return redirect(url_for("index"))
            except sqlite3.IntegrityError:
                error = "El correo ya está registrado"

    return render_template("register.html", error=error)

@app.route("/logout")
def logout():
    session.pop("user", None)
    return redirect(url_for("index"))
@app.route("/arriendos")
def arriendos():
    return render_template("arriendos.html")
# -----------------------------------
# Inicialización
# -----------------------------------
if __name__ == "__main__":
    with app.app_context():
        init_db()  # Crea las tablas si no existen
    app.run(debug=True, port=5000)


