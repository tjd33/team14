# Configure the flask app from here.
#   This way it automagically gets called on startup of the view

from flask import Flask

app = Flask(__name__)
# TODO: Get the config to work correctly
app.config.from_object('senseable_gym.sg_view.config')

from senseable_gym.sg_view import views

# TODO: Include database configuration here
# TODO: Include login configuration here
# TODO: Include openID configuration here
# TODO: Include logging configuration here

# TODO: Configure jinja_env here
# TODO: Import view-wide modules
