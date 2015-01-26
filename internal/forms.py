from datetime import datetime
from wtforms import Form, TextField, RadioField, DateField, PasswordField, validators

class PaymentForm(Form):
    card_number = TextField('Card number', validators=[validators.required('Enter a card number'), validators.length(min=13, max=16, message="Must be a valid credit card number")])
    card_name = TextField('Name on card', validators=[validators.required('Enter the name on the card')])
    expires = TextField('Expires', validators=[validators.required('Enter the expiry date eg 01/15'), validators.regexp('[0-9][0-9]\/[0-9][0-9]', message="Enter expiry date eg 01/15")])
    security_code = TextField('Security code', validators=[validators.required('Enter the security code on the back of your card'), validators.Length(min=3, max=3)])
