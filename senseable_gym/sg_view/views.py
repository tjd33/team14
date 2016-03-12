from datetime import datetime, timedelta

# Non Local Imports
from flask import render_template, redirect
from flask.ext.login import login_user, current_user, logout_user, login_required

# Local Imports
from senseable_gym.sg_view import app, bcrypt
from senseable_gym.sg_view.forms import LoginForm, RegisterForm, ReserveForm, ReserveMachineForm
from senseable_gym.sg_database.database import DatabaseModel
# from senseable_gym.sg_util.machine import Machine, MachineType, MachineStatus
from senseable_gym.sg_util.user import User
from senseable_gym.sg_util.reservation import Reservation
# from senseable_gym.test.basic_example import main
database = DatabaseModel('webTest', 'team14')
# from senseable_gym.sg_util.user_management import delete_user

previous_page = 'test'

@app.route('/machine_view')
@app.route('/machine_view.html/')
def machine_view(db=None):
    global previous_page
    previous_page = '/machine_view'
    # database = DatabaseModel('webTest', 'team14')

    machine_list = database.get_machines()
    user_list = database.get_users()
    print(len(user_list))

    reservation_dict = {}
    for machine in machine_list:
        reservation_dict[machine.machine_id] = database.get_reservations_by_machine(machine)
    return render_template('machine_view.html',
                           machines=machine_list,
                           users=user_list,
                           user=current_user,
                           reservations=reservation_dict
                           )


@app.route('/')
@app.route('/index')
@app.route('/index.html/')
def index():
    global previous_page
    previous_page = '/index'
    
    return render_template('index.html', user=current_user)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():

        try:
            user = database.get_user_from_user_name(form.user.data)
        except:
            user = None
        if user:
            if bcrypt.check_password_hash(user.password, form.password.data):
                user.authenticated = True
                database.session.add(user)
                database.session.commit()
                login_user(user, remember=form.remember_me.data)
                print(user)
                print(current_user)
                print(previous_page)
                return redirect(previous_page)
            else:
                print(str(user) + ' ' + str(user.password))
        else:
            print('no such user')

    return render_template('login.html',
                           title='Sign In',
                           form=form,
                           user=current_user)


@app.route('/logout')
@login_required
def logout():
    global previous_page
    user = current_user
    user = database.get_user(user.user_id)
    user.authenticated = False
    database.session.commit()
    logout_user()
    return redirect(previous_page)


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        if form.password.data == form.repeat_pass.data:
            new_user = User(form.user_name.data,
                            form.first_name.data,
                            form.last_name.data,
                            bcrypt.generate_password_hash(form.password.data))
            database.add_user(new_user)
        return redirect('/index')
    return render_template('register.html', form=form,
                           user=current_user)


@app.route('/reserve', methods=['GET', 'POST'])
def reserve():
    global previous_page
    previous_page = '/index'
    form = ReserveForm()
    machine_list = database.get_machines()
    choices = [(machine.machine_id, machine.machine_id) for machine in machine_list]
    form.machine.choices = choices
    if form.validate_on_submit():
        machine = database.get_machine(form.machine.data)
        start = datetime.combine(form.date.data, form.start_time.data)
        time_delta = timedelta(minutes=form.length.data)
        end = start + time_delta
        reservation = Reservation(machine, current_user, start, end)
        database.add_reservation(reservation)
        return redirect('/index')
    return render_template('reserve.html', form=form, user=current_user)


@app.route('/reserve/<machine_id>', methods=['GET', 'POST'])
def reserve_machine(machine_id=None):
    global previous_page
    previous_page = '/index'
    form = ReserveMachineForm()

    # machine_list = database.get_machines()
    # choices = [(machine.machine_id, machine.machine_id) for machine in machine_list]
    # form.machine.choices = choices

    if form.validate_on_submit():
        machine = database.get_machine(int(machine_id))
        start = datetime.combine(form.date.data, form.start_time.data)
        time_delta = timedelta(minutes=form.length.data)
        end = start + time_delta
        reservation = Reservation(machine, current_user, start, end)
        database.add_reservation(reservation)
        return redirect('/index')
    return render_template('reserve_machine.html', form=form, user=current_user)


@app.route('/settings')
@login_required
def settings():
    global previous_page
    previous_page = '/index'
    return render_template('settings.html', user=current_user)


@app.route('/delete_account')
@login_required
def delete_account():
    user_id = current_user.user_id
    logout()
    database.remove_user(user_id)
    return redirect('/index')


@app.errorhandler(404)
def page_not_found(error):
    return render_template('page_not_found.html'), 404


if __name__ == '__main__':
    # Go to "localhost:5000/" to view pages
    app.debug = True
    app.run()
