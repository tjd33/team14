# Configure the flask app from here.
#   This way it automagically gets called on startup of the view

from flask import Flask

app = Flask(__name__)
app.config('senseable_gym.sg_view.config')

# TODO: Include database configuration here
# TODO: Include login configuration here
# TODO: Include openID configuration here
# TODO: Include logging configuration here

# TODO: Configure jinja_env here
# TODO: Import view-wide modules
