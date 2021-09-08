from flask import Flask, flash, redirect, render_template, url_for
from flask_bcrypt import Bcrypt
from flask_login import LoginManager  # takes care of session in login
from flask_mail import Mail
from flask_sqlalchemy import SQLAlchemy

from flask_blog.config import Config

# create database instance
# to create the file use terminal: from <file name> import <instance name>.
# Here: from flask_blog import db
# and do db.create_all()
# then import User or Post and after doing add & commit a User do for example User.query.first()
db = SQLAlchemy()
bcrypt = Bcrypt()
login_manager = LoginManager()

# this will let the login_required decorator know where the login route is.
# Argument same as in url_for this is the function where the route is located

# Note: easy to miss when using blueprints to set route correctly due to url_for not used
login_manager.login_view = "users.login"
login_manager.login_message_category = "info"

mail = Mail()


# only include the creation of the app & the blueprints, not the extensions
# so the extensions can be used for multiple apps.
# This is why we removed the app as parameters e.g. mail = Mail() instead of Mail(app).
# create_app is our own custom function and set a default config
# Note: in some files app was imported, not this is not possible. Therefore:
# from flask import current_app. And replace app with current_app
def create_app(config_class=Config):
    # __name__ will equal __main__ and this for flask to know where
    # to look for templates & static files and so on
    app = Flask(__name__)

    # this way set configs in a separate file from a class
    app.config.from_object(config_class)

    # config extensions to app
    db.init_app(app)
    bcrypt.init_app(app)
    login_manager.init_app(app)
    mail.init_app(app)

    # This import has been changed because of blueprints. Now importing instance variable of blueprint

    from flask_blog.main.routes import main
    from flask_blog.posts.routes import posts
    from flask_blog.users.routes import users

    app.register_blueprint(users)
    app.register_blueprint(posts)
    app.register_blueprint(main)

    return app
