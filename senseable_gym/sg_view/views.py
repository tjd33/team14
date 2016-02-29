# Non Local Imports
from flask import render_template, redirect, flash
from flask.ext.login import login_user, current_user, logout_user, login_required

# Local Imports
from senseable_gym.sg_view import app
from senseable_gym.sg_view.forms import MyForm, LoginForm, SignupForm
from senseable_gym.sg_database.database import DatabaseModel
from senseable_gym.sg_util.machine import Machine, MachineType, MachineStatus
from senseable_gym.test.basic_example import main

database = DatabaseModel('webTest', 'team14')


@app.route('/machine_view')
@app.route('/machine_view.html/')
def machine_view(db=None):
    
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
    return render_template('index.html', user=current_user)


@app.route('/hello')
@app.route('/hello/<name>')
def hello(name=None):
    return render_template('hello.html', name=name)


@app.route('/example')
def example():
    return render_template('example.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        
        try:
            user = database.get_user_from_user_name(form.user.data)
        except:
            user = None
        if user:
            if user.password == form.password.data:
                user.authenticated = True
                database.session.add(user)
                database.session.commit()
                login_user(user, remember=form.remember_me.data)
                print(user)
                print(current_user)
                return redirect('/index')
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
    user = current_user
    user = database.get_user(user.user_id)
    user.authenticated = False
    database.session.commit()
    logout_user()
    return redirect('/index')

@app.route('/signup', methods=('GET', 'POST'))
def signup():
    form = SignupForm()
    if form.validate_on_submit():
        return redirect('/index')
    return render_template('signup.html', form=form)
    
@app.route('/about')
def about():
    return 'About page'
    
    
@app.route('/reserve')
def reserve():
    return 'reserve page'
    
@app.route('/settings')
def settings():
    return 'settings'
    
@app.route('/form_practice/', methods=('GET', 'POST'))
def form_practice():
    form = MyForm()
    if form.validate_on_submit():
        return redirect('/success')
    return render_template('form_practice.html', form=form)


@app.errorhandler(404)
def page_not_found(error):
    return render_template('page_not_found.html'), 404


if __name__ == '__main__':
    # Go to "localhost:5000/" to view pages
    app.debug = True
    app.run()
