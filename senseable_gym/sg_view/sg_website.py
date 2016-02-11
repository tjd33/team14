#Non Local Imports
from flask import Flask, url_for, render_template

#Local Imports
from senseable_gym.sg_database.database import DatabaseModel
from senseable_gym.sg_util.machine import Machine, MachineType, MachineStatus

app = Flask(__name__)

@app.route('/')
def home():
    db=DatabaseModel('name','ryan')
    machine_1=Machine(MachineType.TREADMILL, [1, 1, 1])
    db.add_machine(machine_1)
    machine_2=Machine(MachineType.TREADMILL, [1, 1, 2])
    db.add_machine(machine_2)
    machine_list=db.get_machines()
    return render_template('machine_view.html', machines=machine_list)

@app.route('/index/')
def index():
    return 'Index Page'

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

@app.errorhandler(404)
def page_not_found(error):
	return render_template('page_not_found.html'), 404

if __name__ == '__main__':
	#go to "localhost:5000/" to view pages
    app.debug = True
    app.run()
    
