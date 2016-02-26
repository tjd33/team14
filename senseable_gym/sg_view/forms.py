from flask_wtf import Form
from wtforms import StringField, BooleanField
from wtforms.validators import DataRequired


class MyForm(Form):
    name = StringField('name', validators=[DataRequired()])
    
class SignupForm(Form):
    user_name = StringField('User Name')
    password = StringField('Password')
    repeat_pass = StringField('Repeat Password')
    
class LoginForm(Form):
    openid = StringField('openid', validators=[DataRequired()])
    remember_me = BooleanField('remember_me', default=False)