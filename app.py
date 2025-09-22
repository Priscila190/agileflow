from flask import Flask, Blueprint, render_template, request, redirect, url_for, session, flash, abort
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
from functools import wraps
import os
import secrets
import bleach

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY') or secrets.token_hex(32)
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL') or 'sqlite:///appointments.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f'<User {self.username}>'


class Appointment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    time = db.Column(db.Time, nullable=False)
    date = db.Column(db.Date, nullable=False)
    attendant = db.Column(db.String(100), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)

    def __repr__(self):
        return f'<Appointment {self.name} on {self.date} at {self.time}>'


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


# ---------------- AUTH ----------------
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
            except Exception:
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


appointments_bp = Blueprint('appointments', __name__)


@appointments_bp.route('/schedule', methods=['GET', 'POST'])
@login_required
def schedule_appointment():
    if request.method == 'POST':
        name = bleach.clean(request.form['name'])
        time = request.form['time']
        date_str = request.form['date']
        attendant = bleach.clean(request.form['attendant'])

        try:
            new_appointment = Appointment(
                name=name,
                time=datetime.strptime(time, '%H:%M').time(),
                date=datetime.strptime(date_str, '%Y-%m-%d').date(),
                attendant=attendant,
                user_id=session.get('user_id')
            )

            db.session.add(new_appointment)
            db.session.commit()
            flash('Compromisso agendado com sucesso!', 'success')
            return redirect('/appointments')
        except ValueError:
            flash('Erro nos dados fornecidos. Verifique a data e hora.', 'error')
        except Exception:
            db.session.rollback()
            flash('Erro ao criar agendamento. Tente novamente.', 'error')

    return render_template('system/schedule_appointment.html')


@appointments_bp.route('/appointments')
@login_required
def appointment_list():
    appointments = Appointment.query.order_by(
        Appointment.date.desc(),
        Appointment.time.desc()
    ).all()

    total_appointments = len(appointments)

    today = datetime.now().date()
    today_appointments = Appointment.query.filter(Appointment.date == today).all()
    today_appointments_count = len(today_appointments)

    now = datetime.now().time()
    time_limit = (datetime.now() + timedelta(minutes=30)).time()

    next_appointments_today = Appointment.query.filter(
        Appointment.date == today,
        Appointment.time >= now,
        Appointment.time <= time_limit
    ).order_by(Appointment.time.asc()).all()

    expired_appointments = Appointment.query.filter(
        (Appointment.date < today) |
        ((Appointment.date == today) & (Appointment.time < now))
    ).all()
    expired_appointments_count = len(expired_appointments)

    return render_template(
        'system/appointment_list.html',
        appointments=appointments,
        total_appointments=total_appointments,
        today_appointments_count=today_appointments_count,
        next_appointments_today=next_appointments_today,
        expired_appointments_count=expired_appointments_count
    )


@appointments_bp.route('/my-appointments')
@login_required
def my_appointments():
    user_id = current_user_id()

    appointments = Appointment.query.filter_by(user_id=user_id).order_by(
        Appointment.date.desc(),
        Appointment.time.desc()
    ).all()

    total_appointments = len(appointments)

    today = datetime.now().date()
    now = datetime.now().time()

    today_appointments = Appointment.query.filter(
        Appointment.user_id == user_id,
        Appointment.date == today
    ).all()
    today_appointments_count = len(today_appointments)

    time_limit = (datetime.now() + timedelta(minutes=30)).time()
    next_appointments_today = Appointment.query.filter(
        Appointment.user_id == user_id,
        Appointment.date == today,
        Appointment.time >= now,
        Appointment.time <= time_limit
    ).order_by(Appointment.time.asc()).all()

    expired_appointments = Appointment.query.filter(
        Appointment.user_id == user_id,
        ((Appointment.date < today) |
         ((Appointment.date == today) & (Appointment.time < now)))
    ).all()
    expired_appointments_count = len(expired_appointments)

    return render_template(
        'system/appointment_list.html',
        appointments=appointments,
        total_appointments=total_appointments,
        today_appointments_count=today_appointments_count,
        next_appointments_today=next_appointments_today,
        expired_appointments_count=expired_appointments_count
    )

@app.errorhandler(404)
def page_not_found(e):
    flash('Página não encontrada. Você foi redirecionado para a página inicial.', 'warning')
    return redirect(url_for('index'))

@app.route('/')
def index():
    return render_template('index.html')


app.register_blueprint(auth_bp, url_prefix='/auth')
app.register_blueprint(appointments_bp)

with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run(debug=True)
