#Non Local Imports
from flask import Flask, url_for, render_template

#Local Imports
from senseable_gym.sg_database.database import DatabaseModel

app = Flask(__name__)

@app.route('/')
def home():
    machines = DatabaseModel.get_machines()
    return render_template('machine_view.html', machines=machines)

@app.route('/index/')
def index():
    return 'Index Page'

@app.route('/hello/')
@app.route('/hello/<name>')
def hello(name=None):
    return render_template('hello.html', name=name)

@app.route('/admin/')
def admin():
    return 'Admin Page'

@app.route('/login/')
def login():
    return 'Login Page'

@app.errorhandler(404)
def page_not_found(error):
	return render_template('page_not_found.html'), 404

if __name__ == '__main__':
    app.debug = True
    app.run()
    
