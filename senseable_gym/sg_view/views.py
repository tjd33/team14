from datetime import datetime, timedelta

# Non Local Imports
from flask import render_template, redirect, jsonify
from flask.ext.login import login_user, current_user, logout_user, login_required

# Local Imports
from senseable_gym.sg_view import app, bcrypt
from senseable_gym.sg_view.forms import LoginForm, RegisterForm, ReserveForm, ReserveMachineForm, EditUserForm
from senseable_gym.sg_database.database import DatabaseModel
# from senseable_gym.sg_util.machine import Machine, MachineType, MachineStatus
from senseable_gym.sg_util.user import User
from senseable_gym.sg_util.reservation import Reservation
from senseable_gym.sg_util.exception import ReservationError
# from senseable_gym.test.basic_example import main
database = DatabaseModel('webTest', 'team14')
# from senseable_gym.sg_util.user_management import delete_user

previous_page = '/index'


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
                return redirect(previous_page)
            else:
                form.password.errors.append('Password does not match user')
        else:
            print('no such user')
            form.user.errors.append("Username does not exist")

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
            try:
                database.get_user_from_user_name(form.user_name.data)
                form.user_name.errors.append('Username already in use')
            except:
                new_user = User(form.user_name.data,
                                form.first_name.data,
                                form.last_name.data,
                                bcrypt.generate_password_hash(form.password.data))
                new_user.authenticated = True
                database.add_user(new_user)
                database.session.add(new_user)
                database.session.commit()
                login_user(new_user)
                return redirect('/index')
        else:
            form.repeat_pass.errors.append('Passwords do not match')
    return render_template('register.html', form=form,
                           user=current_user)


@app.route('/reserve', methods=['GET', 'POST'])
@login_required
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
        try:
            database.add_reservation(reservation)
        except ReservationError:
            form.start_time.errors.append("Reservation time overlaps with existing reservation")
            return render_template('reserve.html', form=form, user=current_user)
        return redirect('/machine_view')
    return render_template('reserve.html', form=form, user=current_user)


@app.route('/reserve/<machine_id>', methods=['GET', 'POST'])
@login_required
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
        try:
            database.add_reservation(reservation)
        except ReservationError:
            form.start_time.errors.append("Reservation time overlaps with existing reservation")
            return render_template('reserve.html', form=form, user=current_user)
        return redirect('/machine_view')
    return render_template('reserve.html', form=form, user=current_user)


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


@app.route('/edit_user', methods=['GET', 'POST'])
@login_required
def edit_user():
    form = EditUserForm()
    if form.validate_on_submit():
        user = current_user
        change = False

        print(form.user_name.data)
        print(user.user_name)
        if form.user_name.data != user.user_name:
            try:
                database.get_user_from_user_name(form.user_name.data)
                form.user_name.errors.append('Username already in use')
                return render_template('edit_user.html', form=form,
                                       user=current_user)
            except:
                change = True
        if form.first_name.data != user.first_name or form.last_name.data != user.last_name:
            change = True
        if form.password.data != '':
            passhash = bcrypt.generate_password_hash(form.password.data)
            if form.password.data == form.repeat_pass.data:
                change = True
            else:
                form.repeat_pass.error.append('Passwords do not match')
                return render_template('edit_user.html', form=form,
                                       user=current_user)
        print(change)

        if change:
            user = database.get_user(user.user_id)
            user.user_name = form.user_name.data
            if form.password.data != '':
                user.password = passhash
            user.first_name = form.first_name.data
            user.last_name = form.last_name.data
            database.session.commit()
            login_user(user)
            return redirect('/settings')
        else:
            form.user_name.errors.append('Nothing has been changed')
    else:
        form.user_name.data = current_user.user_name
        form.first_name.data = current_user.first_name
        form.last_name.data = current_user.last_name

    return render_template('edit_user.html', form=form,
                           user=current_user)


@app.route('/user_reservations')
@login_required
def user_reservations():
    reservations = database.get_reservations_by_user(current_user)
    machine_list = database.get_machines()
    machines = {machine.machine_id: machine for machine in machine_list}
    return render_template('user_reservations.html',
                           user=current_user,
                           reservations=reservations,
                           machines=machines)


@app.route('/_reservation_list/<machine_id>')
def get_reservation_dict(machine_id):
    machine = database.get_machine(machine_id)
    res_list = database.get_applicable_reservations_by_machine(machine, datetime.now() + timedelta(days=1))
    res_dict = {'machine_id': int(machine_id)}
    res_dict['reservations'] = [
            {
                'start_time': res.start_time.strftime("%d, %B %Y %I:%M%p"),
                'end_time': res.end_time.strftime("%d, %B %Y %I:%M%p"),
            }
            for res in res_list
            ]
    return jsonify(res_dict)


@app.errorhandler(404)
def page_not_found(error):
    return render_template('page_not_found.html'), 404

if __name__ == '__main__':
    # Go to "localhost:5000/" to view pages
    app.debug = True
    app.run()
