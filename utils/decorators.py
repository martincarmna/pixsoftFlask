from functools import wraps
from flask import session, redirect, url_for

def admin_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if session.get("user_email") != "admin@pixsoft.com":
            return "No tienes permisos", 403
        return f(*args, **kwargs)
    return wrapper

def login_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if not session.get("user_email"):
            return redirect(url_for("auth.loginuser"))
        return f(*args, **kwargs)
    return wrapper
