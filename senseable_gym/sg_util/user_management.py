from flask.ext.login import current_user

from senseable_gym.sg_view import app, bcrypt
from senseable_gym.sg_view.views import database


def delete_user():
    database.remove_user(current_user.user_id)
    current_user = None