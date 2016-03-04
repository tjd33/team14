from datetime import datetime

from flask_wtf import Form
from wtforms import StringField, BooleanField, TextField, PasswordField, SelectField, IntegerField
from wtforms.validators import DataRequired
from wtforms.fields.html5 import DateField
from wtforms_components import TimeField



class MyForm(Form):
    name = StringField('name', validators=[DataRequired()])
    
class SignupForm(Form):
    user_name = TextField('User Name', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    repeat_pass = PasswordField('Repeat Password', validators=[DataRequired()])
    first_name = TextField('First Name', validators=[DataRequired()])
    last_name = TextField('Last Name', validators=[DataRequired()])
    
class LoginForm(Form):
    user = TextField('User', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me', default=False)
    
class ReserveForm(Form):
    machine = SelectField('Machine', coerce=int)
    date = DateField('Date', format='%Y-%m-%d', default=datetime.today())
    start_time = TimeField('Start time', default = datetime.now())
    length = IntegerField('Duration in minutes', default=30)