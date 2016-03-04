from flask_wtf import Form
from wtforms import StringField, BooleanField, TextField, PasswordField
from wtforms.validators import DataRequired


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
    password = PasswordField('Passwlrd', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me', default=False)