from functools import wraps
from flask import session, redirect, url_for, flash, request, abort

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Você precisa estar logado para acessar esta página.', 'warning')
            return redirect(url_for('auth.login', next=request.url))
        return f(*args, **kwargs)
    return decorated_function


def current_user_id():
    user_id = session.get('user_id')
    if not user_id:
        abort(403)
    return user_id