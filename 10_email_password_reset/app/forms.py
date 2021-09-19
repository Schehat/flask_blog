from flask import flash
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from flask_login import current_user

# these are possible types of fields
from wtforms import StringField, PasswordField, SubmitField, BooleanField, TextAreaField

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

    # custom validators. Naming convention otherwise it will not work is: validate_<field>
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


class UpdateAccountForm(FlaskForm):
    # first argument name of the field. Here: Username will be labeled in html
    # validation: restriction to the fields. DataRequired() handles that it won't be empty
    username = StringField(
        "Username", validators=[DataRequired(), Length(min=2, max=20)]
    )
    email = StringField("Email", validators=[DataRequired(), Email()])
    picture = FileField(
        "Update Profile Picture", validators=[FileAllowed(["jpg", "png"])]
    )
    submit = SubmitField("Update")

    # custom validators
    # check if username already exists
    def validate_username(self, username):
        if username.data != current_user.username:
            user = User.query.filter_by(username=username.data).first()
            if user:
                raise ValidationError(
                    "That username is taken. Please choose a different one."
                )

    def validate_email(self, email):
        if email.data != current_user.email:
            user = User.query.filter_by(email=email.data).first()
            if user:
                raise ValidationError(
                    "That email is taken. Please choose a different one."
                )


class PostForm(FlaskForm):
    title = StringField("Title", validators=[DataRequired()])
    content = TextAreaField("Content", validators=[DataRequired()])
    submit = SubmitField("Post")


class RequestResetForm(FlaskForm):
    email = StringField("Email", validators=[DataRequired(), Email()])
    submit = SubmitField("Request Password Reset")

    def validate_email(self, email):
        # bad practice for security. Because this allows
        # enumeration attacks by telling if an account exists
        # user = User.query.filter_by(email=email.data).first()
        # if user is None:
        #     raise ValidationError(
        #         "There is no account with this email. You must Register first"
        #     )

        # rather display to which email the reset was sended, so the user can check if email correct
        flash(f"The reset link was sended to this email address: {email.data}", "info")


class ResetPasswordForm(FlaskForm):
    password = PasswordField("Password", validators=[DataRequired()])
    confirm_password = PasswordField(
        "Confirm Password", validators=[DataRequired(), EqualTo("password")]
    )
    submit = SubmitField("Reset Password")
