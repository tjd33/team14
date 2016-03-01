from flask_wtf import Form
from wtforms import StringField, BooleanField
from wtforms.validators import DataRequired


class MyForm(Form):
    name = StringField('name', validators=[DataRequired()])
    
class SignupForm(Form):
    user_name = StringField('User Name', validators=[DataRequired()])
    password = StringField('Password', validators=[DataRequired()])
    repeat_pass = StringField('Repeat Password', validators=[DataRequired()])
    first_name = StringField('First Name', validators=[DataRequired()])
    last_name = StringField('Last Name', validators=[DataRequired()])
    
class LoginForm(Form):
    user = StringField('User', validators=[DataRequired()])
    password = StringField('Passwlrd', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me', default=False)