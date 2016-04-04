from datetime import datetime, timedelta

from flask_wtf import Form
from wtforms import StringField, BooleanField, TextField, PasswordField, SelectField, IntegerField
from wtforms.validators import DataRequired
from wtforms.fields.html5 import DateField
from wtforms_components import TimeField


class MyForm(Form):
    name = StringField('name', validators=[DataRequired()])


class RegisterForm(Form):
    user_name = TextField('User Name', validators=[DataRequired()], render_kw={"placeholder": "Username"})
    password = PasswordField('Password', validators=[DataRequired()], render_kw={"placeholder": "Password"})
    repeat_pass = PasswordField('Repeat Password', validators=[DataRequired()], render_kw={"placeholder": "Confirm Password"})
    first_name = TextField('First Name', validators=[DataRequired()], render_kw={"placeholder": "First Name"})
    last_name = TextField('Last Name', validators=[DataRequired()], render_kw={"placeholder": "Last Name"})
    

class LoginForm(Form):
    user = TextField('User', validators=[DataRequired()], render_kw={"placeholder": "Username"})
    password = PasswordField('Password', validators=[DataRequired()], render_kw={"placeholder": "Password"})
    remember_me = BooleanField('Remember Me', default=False)


class ReserveForm(Form):
    machine = SelectField('Machine', coerce=int)
    date = DateField('Date', format='%Y-%m-%d', default=datetime.today(), validators=[DataRequired()])
    start_time = TimeField('Start time', default=datetime.now(), validators=[DataRequired()])
    length = IntegerField('Duration in minutes', default=30, validators=[DataRequired()])


class ReserveMachineForm(Form):
    date = DateField('Date', format='%Y-%m-%d', default=datetime.today(), validators=[DataRequired()])
    start_time = TimeField('Start time', default=datetime.now(), validators=[DataRequired()])
    length = IntegerField('Duration in minutes', default=30, validators=[DataRequired()])

class EditUserForm(Form):
    user_name = TextField('User Name', validators=[DataRequired()], render_kw={"placeholder": "Username"})
    password = PasswordField('Password', render_kw={"placeholder": "New Password"})
    repeat_pass = PasswordField('Repeat Password', render_kw={"placeholder": "Confirm Password"})
    first_name = TextField('First Name', validators=[DataRequired()], render_kw={"placeholder": "First Name"})
    last_name = TextField('Last Name', validators=[DataRequired()], render_kw={"placeholder": "Last Name"})

class EditMachineForm(Form):
    machine_type = SelectField('Type', coerce=int)
    position_x = IntegerField('X coordinate')
    position_y = IntegerField('Y coordinate')
    position_z = IntegerField('Z coordinate')
    
class TimePeriodForm(Form):
    date = DateField('Date', format='%Y-%m-%d', default=datetime.today(), validators=[DataRequired()])
    start_time = TimeField('Start time', default=datetime.now(), validators=[DataRequired()])
    end_time = TimeField('End time', default=datetime.now()+timedelta(hours=1), validators=[DataRequired()])
    
class EditReservationForm(Form):
    machine = SelectField('Machine', coerce=int)
    date = DateField('Date', format='%Y-%m-%d', validators=[DataRequired()])
    start_time = TimeField('Start time', validators=[DataRequired()])
    end_time = TimeField('End time', validators=[DataRequired()])
    
class AdminPasswordForm(Form):
    password = PasswordField('Password', validators=[DataRequired()], render_kw={"placeholder": "Password"})

class AddAdminForm(Form):
    user = TextField('User', validators=[DataRequired()], render_kw={"placeholder": "Username"})
    