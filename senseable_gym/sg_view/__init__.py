# Configure the flask app from here.
#   This way it automagically gets called on startup of the view

from flask import Flask

app = Flask(__name__)
# TODO: Get the config to work correctly
app.config.from_object('senseable_gym.sg_view.config')

from senseable_gym.sg_view import views

# create database

# TODO: Include database configuration here
login_manager = LoginManager()
login_manager.init_app(app)
@login_manager.user_loader
def load_user(user_id):
    # database get/add user
    return user 
# TODO: Include openID configuration here
# TODO: Include logging configuration here

# TODO: Configure jinja_env here
# TODO: Import view-wide modules
