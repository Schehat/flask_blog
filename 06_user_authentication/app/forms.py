from flask_wtf import FlaskForm

# these are possible types of fields
from wtforms import StringField, PasswordField, SubmitField, BooleanField

# for validation in fields. These are the desired parameters
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
from app.models import User

# elements in class are fields, which are imported classes
class RegistrationForm(FlaskForm):
    # first argument name of the field. Here: Username will be labeled in html
    # validation: restriction to the fields. DataRequired() handles that it won't be empty
    username = StringField(
        "Username", validators=[DataRequired(), Length(min=2, max=20)]
    )
    email = StringField("Email", validators=[DataRequired(), Email()])
    password = PasswordField("Password", validators=[DataRequired()])
    # EqualTo validator argument: which field should it be equal to, here: password
    confirm_password = PasswordField(
        "Confirm Password", validators=[DataRequired(), EqualTo("password")]
    )
    submit = SubmitField("Sign Up")

    # custom validators
    # check if username already exists
    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError(
                "That username is taken. Please choose a different one."
            )

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError("That email is taken. Please choose a different one.")


class LoginForm(FlaskForm):
    email = StringField("Email", validators=[DataRequired(), Email()])
    password = PasswordField("Password", validators=[DataRequired()])
    # remember: the login with a cookie later
    remember = BooleanField("Remember me")
    submit = SubmitField("Login")
