import os
import secrets  # to generate random hex

from flask import current_app, url_for
from flask_blog import mail
from flask_blog.models import User
from flask_login import current_user
from flask_mail import Message
from PIL import Image


def save_picture(form_picture):
    random_hex = secrets.token_hex(8)  # generate random name for uploaded file
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ext
    picture_path = os.path.join(current_app.root_path, "static", picture_fn)

    # delete current picture in memory
    current_picture_path = (
        User.query.filter(User.email == current_user.email).first().image_file
    )
    os.remove(os.path.join(current_app.root_path, "static", current_picture_path))

    # scale down picture
    output_size = (125, 125)
    i = Image.open(form_picture)
    i.thumbnail(output_size)
    i.save(picture_path)

    return picture_fn


def send_reset_email(user):
    token = user.get_reset_token()
    # arguments:
    # 1: title of mail
    # sender: what email address will be shown to the user
    msg = Message(
        "Password  Reset Request",
        sender="flask_blog_reset@outlook.de",
        recipients=[user.email],
    )
    # _external: tells flask to use instead of a relative path, the absolute path.
    # Otherwise the link would not work. In the page itself relative links are ok but in an email
    msg.body = f"""To reset your password, visit the following link:
{url_for('users.reset_token', token=token, _external=True)}

If you did not make this request then simply ignore this email and no changes will be made.
"""
    mail.send(msg)
