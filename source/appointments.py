from flask import Blueprint, render_template, request, redirect, session, flash, abort
from source.models import db, Appointment
from source.decorators import login_required, current_user_id
from datetime import datetime, timedelta
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
            existing_appointment = Appointment.query.filter_by(
                date=datetime.strptime(date_str, '%Y-%m-%d').date(),
                time=datetime.strptime(time, '%H:%M').time(),
                user_id=session.get('user_id')
            ).first()

            if existing_appointment:
                flash('Você já tem um compromisso agendado para este horário.', 'error')
                return render_template('system/schedule_appointment.html')

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
            return redirect('/my-appointments')
        except ValueError:
            flash('Erro nos dados fornecidos. Verifique a data e hora.', 'error')
        except Exception as e:
            flash('Erro ao criar agendamento. Tente novamente.', 'error')
            db.session.rollback()

    min_date = datetime.now().strftime('%Y-%m-%d')
    return render_template('system/schedule_appointment.html', min_date=min_date)


@appointments_bp.route('/appointments')
@login_required
def appointment_list():
    return redirect('/my-appointments')


@appointments_bp.route('/my-appointments')
@login_required
def my_appointments():
    user_id = current_user_id()

    appointments = Appointment.query.filter_by(user_id=user_id).order_by(
        Appointment.date.asc(),
        Appointment.time.asc()
    ).all()

    total_appointments = len(appointments)

    today = datetime.now().date()
    now = datetime.now().time()
    time_limit = (datetime.now() + timedelta(minutes=30)).time()

    today_appointments = [a for a in appointments if a.date == today]
    today_appointments_count = len(today_appointments)

    next_appointments_today = [a for a in today_appointments if a.time >= now]
    next_appointments_today.sort(key=lambda x: x.time)

    future_appointments = [a for a in appointments if a.date > today]
    future_appointments.sort(key=lambda x: (x.date, x.time))

    past_appointments = [a for a in appointments if a.date < today or (a.date == today and a.time < now)]
    past_appointments_count = len(past_appointments)

    return render_template('system/appointment_list.html',
                           appointments=appointments,
                           total_appointments=total_appointments,
                           today_appointments_count=today_appointments_count,
                           next_appointments_today=next_appointments_today,
                           past_appointments_count=past_appointments_count,
                           future_appointments=future_appointments,
                           past_appointments=past_appointments,
                           today_appointments=today_appointments)


@appointments_bp.route('/appointments/edit/<int:appointment_id>', methods=['GET', 'POST'])
@login_required
def edit_appointment(appointment_id):
    appointment = Appointment.query.get_or_404(appointment_id)

    if appointment.user_id != session.get('user_id'):
        abort(403)

    if request.method == 'POST':
        appointment.name = bleach.clean(request.form['name'])
        appointment.attendant = bleach.clean(request.form['attendant'])
        try:
            appointment.time = datetime.strptime(request.form['time'], '%H:%M').time()
            appointment.date = datetime.strptime(request.form['date'], '%Y-%m-%d').date()
            db.session.commit()
            flash('Compromisso atualizado com sucesso!', 'success')
            return redirect('/my-appointments')
        except ValueError:
            flash('Erro nos dados fornecidos. Verifique a data e hora.', 'error')
        except Exception:
            flash('Erro ao atualizar compromisso. Tente novamente.', 'error')
            db.session.rollback()

    appointment_date = appointment.date.strftime('%Y-%m-%d')
    appointment_time = appointment.time.strftime('%H:%M')
    min_date = datetime.now().strftime('%Y-%m-%d')

    return render_template('system/edit_list.html',
                           appointment=appointment,
                           appointment_date=appointment_date,
                           appointment_time=appointment_time,
                           min_date=min_date)


@appointments_bp.route('/appointments/delete/<int:appointment_id>', methods=['POST'])
@login_required
def delete_appointment(appointment_id):
    appointment = Appointment.query.get_or_404(appointment_id)

    if appointment.user_id != session.get('user_id'):
        abort(403)

    try:
        db.session.delete(appointment)
        db.session.commit()
        flash('Compromisso excluído com sucesso!', 'success')
    except Exception:
        db.session.rollback()
        flash('Erro ao excluir compromisso. Tente novamente.', 'error')

    return redirect('/my-appointments')