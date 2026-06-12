from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, ValidationError
from wtforms.validators import Length, EqualTo, Email, DataRequired
from shop.models import User

class SignupForm(FlaskForm):
    username = StringField(label='User Name', validators=[Length(min=2,max=30),DataRequired()])
    email= StringField(label='Email Id',validators=[Email()])
    password1= PasswordField(label='Password',validators=[Length(min=6)])
    password2= PasswordField(label='Confirm password',validators=[EqualTo('password1')])
    
    def validate_username(self,username_to_check):
        user=User.query.filter_by(username=username_to_check.data).first()
    
        if user:
            raise ValidationError('Username already exists! Please try a different username')
    
    def validate_email(self,email_to_check):
        email=User.query.filter_by(email=email_to_check.data).first()
    
        if email:
            raise ValidationError('Email already exists! Please try a different email')


class LoginForm(FlaskForm):
      username = StringField(label='User Name', validators=[DataRequired()])
      password= PasswordField(label='Password',validators=[DataRequired()])