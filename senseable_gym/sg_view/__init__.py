# Configure the flask app from here.
#   This way it automagically gets called on startup of the view

from flask import Flask
from flask.ext.login import LoginManager
from flask.ext.bcrypt import Bcrypt


app = Flask(__name__)
# TODO: Get the config to work correctly
app.config.from_object('senseable_gym.sg_view.config')


from senseable_gym.sg_database.database import DatabaseModel
from senseable_gym.test.basic_example import main

database = main(level='INFO', dbname='webTest')

# TODO: Include database configuration here
login_manager = LoginManager()
login_manager.init_app(app)
@login_manager.user_loader
def load_user(user_id):
    users = database.get_users()
    user = users[0]
    return user 
    
# TODO: Include openID configuration here
# TODO: Include logging configuration here

# TODO: Configure jinja_env here
# TODO: Import view-wide modules


bcrypt = Bcrypt(app)

from senseable_gym.sg_view import views