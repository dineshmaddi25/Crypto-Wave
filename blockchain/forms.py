from wtforms import Form, StringField, PasswordField, validators, DecimalField

class RegisterForm(Form):
    name = StringField('Name', [validators.Length(min=1, max=50)])
    email = StringField('Email', [validators.Length(min=6, max=50)])
    username = StringField('Username', [validators.Length(min=4, max=25)])
    password = PasswordField('Password', [
        validators.DataRequired(),
        validators.EqualTo('confirm', message='Passwords do not match')
    ])
    confirm = PasswordField('Confirm Password')

class SendMoneyForm(Form):
    username = StringField('Username', [validators.Length(min=4, max=25)])
    amount = DecimalField('Amount', [validators.NumberRange(min=0.01)])

class BuyForm(Form):
    amount = DecimalField('Amount', [validators.NumberRange(min=0.01)])
