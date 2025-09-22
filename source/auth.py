from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from source.models import db, User
from source.decorators import login_required
import bleach

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        session.clear()

        username = bleach.clean(request.form.get('username', ''))
        password = request.form.get('password', '')

        user = User.query.filter_by(username=username).first()

        if user and user.check_password(password):
            session['user_id'] = user.id
            session['username'] = user.username
            flash('Login realizado com sucesso!', 'success')
            next_page = request.args.get('next')
            return redirect(next_page or url_for('appointments.my_appointments'))
        else:
            flash('Usuário ou senha incorretos.', 'error')

    return render_template('auth/login.html')


@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = bleach.clean(request.form['username'])
        email = bleach.clean(request.form['email'])
        password = request.form['password']
        confirm_password = request.form['confirm_password']

        errors = []

        if len(username) < 3:
            errors.append('O nome de usuário deve ter pelo menos 3 caracteres.')
        elif User.query.filter_by(username=username).first():
            errors.append('Nome de usuário já existe.')

        if User.query.filter_by(email=email).first():
            errors.append('Email já está em uso.')

        if len(password) < 6:
            errors.append('A senha deve ter pelo menos 6 caracteres.')

        if password != confirm_password:
            errors.append('As senhas não coincidem.')

        if errors:
            for error in errors:
                flash(error, 'error')
        else:
            new_user = User(username=username, email=email)
            new_user.set_password(password)

            try:
                db.session.add(new_user)
                db.session.commit()
                flash('Conta criada com sucesso! Agora você pode fazer login.', 'success')
                return redirect(url_for('auth.login'))
            except Exception as e:
                db.session.rollback()
                flash('Erro ao criar conta. Tente novamente.', 'error')

    return render_template('auth/register.html')

@auth_bp.route('/logout')
@login_required
def logout():
    username = session.get('username', 'Usuário')
    session.clear()
    flash(f'Logout realizado com sucesso, {username}!', 'success')
    return redirect(url_for('auth.login'))

