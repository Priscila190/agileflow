from flask import Blueprint, render_template, request, redirect, session, flash, abort, url_for
from source.models import db, Appointment, User
from source.decorators import login_required, current_user_id
from datetime import datetime, timedelta
import bleach

appointments_bp = Blueprint('appointments', __name__)
auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/update_password', methods=['GET', 'POST'])
@login_required
def update_password():
    if request.method == 'POST':
        current_password = request.form.get('current_password', '')
        new_password = request.form.get('new_password', '')
        confirm_password = request.form.get('confirm_password', '')

        user = User.query.get(session['user_id'])

        if not user.check_password(current_password):
            flash('Senha atual incorreta.', 'error')
            return redirect(url_for('auth.update_password'))

        if len(new_password) < 6:
            flash('A nova senha deve ter pelo menos 6 caracteres.', 'error')
        elif new_password != confirm_password:
            flash('As senhas não coincidem.', 'error')
        else:
            user.set_password(new_password)
            try:
                db.session.commit()
                flash('Senha atualizada com sucesso!', 'success')
                return redirect(url_for('appointments.my_appointments'))
            except Exception:
                db.session.rollback()
                flash('Erro ao atualizar a senha. Tente novamente.', 'error')

    return render_template('auth/update_password.html')


@appointments_bp.route('/schedule', methods=['GET', 'POST'])
@login_required
def schedule_appointment():
    if request.method == 'POST':
        name = bleach.clean(request.form['name'])
        time_str = request.form['time']
        date_str = request.form['date']
        attendant = bleach.clean(request.form['attendant'])

        try:
            appointment_time = datetime.strptime(time_str, '%H:%M').time()
            appointment_date = datetime.strptime(date_str, '%Y-%m-%d').date()

            existing_appointment = Appointment.query.filter_by(
                date=appointment_date,
                time=appointment_time,
                user_id=session.get('user_id')
            ).first()

            if existing_appointment:
                flash('Você já tem um compromisso agendado para este horário.', 'error')
                return render_template('system/schedule_appointment.html', min_date=date_str)

            new_appointment = Appointment(
                name=name,
                time=appointment_time,
                date=appointment_date,
                attendant=attendant,
                user_id=session.get('user_id')
            )
            db.session.add(new_appointment)
            db.session.commit()
            flash('Compromisso agendado com sucesso!', 'success')
            return redirect(url_for('appointments.my_appointments'))
        except ValueError:
            flash('Erro nos dados fornecidos. Verifique a data e hora.', 'error')
        except Exception:
            db.session.rollback()
            flash('Erro ao criar agendamento. Tente novamente.', 'error')

    min_date = datetime.now().strftime('%Y-%m-%d')
    return render_template('system/schedule_appointment.html', min_date=min_date)


@appointments_bp.route('/appointments')
@login_required
def appointment_list():
    return redirect(url_for('appointments.my_appointments'))


@appointments_bp.route('/my-appointments')
@login_required
def my_appointments():
    user_id = current_user_id()
    appointments = Appointment.query.filter_by(user_id=user_id).order_by(Appointment.date.asc(),
                                                                         Appointment.time.asc()).all()

    today = datetime.now().date()
    now = datetime.now().time()

    today_appointments = [a for a in appointments if a.date == today]
    next_appointments_today = sorted([a for a in today_appointments if a.time >= now], key=lambda x: x.time)
    future_appointments = sorted([a for a in appointments if a.date > today], key=lambda x: (x.date, x.time))
    past_appointments = [a for a in appointments if a.date < today or (a.date == today and a.time < now)]

    return render_template('system/appointment_list.html',
                           appointments=appointments,
                           total_appointments=len(appointments),
                           today_appointments_count=len(today_appointments),
                           next_appointments_today=next_appointments_today,
                           past_appointments_count=len(past_appointments),
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
            return redirect(url_for('appointments.my_appointments'))
        except ValueError:
            flash('Erro nos dados fornecidos. Verifique a data e hora.', 'error')
        except Exception:
            db.session.rollback()
            flash('Erro ao atualizar compromisso. Tente novamente.', 'error')

    return render_template('system/edit_list.html',
                           appointment=appointment,
                           appointment_date=appointment.date.strftime('%Y-%m-%d'),
                           appointment_time=appointment.time.strftime('%H:%M'),
                           min_date=datetime.now().strftime('%Y-%m-%d'))


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

    return redirect(url_for('appointments.my_appointments'))
