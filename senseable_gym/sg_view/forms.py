from flask_wtf import Form
from wtforms import StringField
from wtforms.validators import DataRequired


class MyForm(Form):
    name = StringField('name', validators=[DataRequired()])
