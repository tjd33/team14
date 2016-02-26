# Non Local Imports
from flask import render_template, redirect

# Local Imports
from senseable_gym.sg_view import app
from senseable_gym.sg_view.forms import MyForm
from senseable_gym.sg_database.database import DatabaseModel
from senseable_gym.sg_util.machine import Machine, MachineType, MachineStatus
from senseable_gym.test.basic_example import main


@app.route('/machine_view')
def home(database=None):
    if database is None:
        db = main(level='INFO', dbname='none')
    else:
        db = DatabaseModel(None, 'ryan')

        machine_1 = Machine(MachineType.TREADMILL, [1, 1, 1])
        machine_1.status = MachineStatus.BUSY
        db.add_machine(machine_1)
        machine_2 = Machine(MachineType.TREADMILL, [1, 1, 2])
        db.add_machine(machine_2)

    machine_list = db.get_machines()
    user_list = db.get_users()

    reservation_dict = {}
    for machine in machine_list:
        reservation_dict[machine.machine_id] = db.get_reservations_by_machine(machine)
    return render_template('machine_view.html',
                           machines=machine_list,
                           users=user_list,
                           reservations=reservation_dict
                           )

@app.route('/')            
@app.route('/index/')
def index():
    user = None
    return render_template('index.html', user=user)


@app.route('/hello/')
@app.route('/hello/<name>')
def hello(name=None):
    return render_template('hello.html', name=name)


@app.route('/example/')
def example():
    return render_template('example.html')


@app.route('/login/')
def login():
    return 'Login Page'


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
