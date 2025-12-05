from flask import Blueprint, request, session, redirect, url_for, render_template
from models.db import get_db

bp = Blueprint("auth", __name__, url_prefix="/auth")

@bp.route("/login", methods=["GET", "POST"])
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
                return redirect(url_for("admin.admin_productos"))
            return redirect(url_for("public.index"))
        else:
            error = "Usuario o contraseña incorrectos"
    return render_template("loginuser.html", error=error)

@bp.route("/logout")
def logout():
    session.pop("user", None)
    session.pop("user_email", None)
    return redirect(url_for("public.index"))

@bp.route("/register", methods=["GET", "POST"])
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
                return redirect(url_for("public.index"))
            except:
                error = "El correo ya está registrado"
    return render_template("register.html", error=error)
