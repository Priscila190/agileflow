from flask import Blueprint, render_template, request, redirect, session, flash
from source.models import db, Appointment
from source.decorators import login_required, current_user_id
from datetime import datetime, timedelta, date
import bleach

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
        except ValueError as e:
            flash('Erro nos dados fornecidos. Verifique a data e hora.', 'error')
        except Exception as e:
            flash('Erro ao criar agendamento. Tente novamente.', 'error')
            db.session.rollback()

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
    today_appointments = Appointment.query.filter(
        Appointment.date == today
    ).all()
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

    return render_template('system/appointment_list.html',
                           appointments=appointments,
                           total_appointments=total_appointments,
                           today_appointments_count=today_appointments_count,
                           next_appointments_today=next_appointments_today,
                           expired_appointments_count=expired_appointments_count)


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

    return render_template('system/appointment_list.html',
                           appointments=appointments,
                           total_appointments=total_appointments,
                           today_appointments_count=today_appointments_count,
                           next_appointments_today=next_appointments_today,
                           expired_appointments_count=expired_appointments_count)




