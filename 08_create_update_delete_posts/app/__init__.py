from flask import Flask, render_template, url_for, flash, redirect
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager  # takes care of session in login

# __name__ will equal __main__ and this for flask to know where
# to look for templates & static files and so on
app = Flask(__name__)
# for security meseaures to prevent CSRF attacks. Set of random character
app.config["SECRET_KEY"] = "c199a4bd65fd34f90e38674dde8f8703"
# set location of database. Triple slash(///) is for relative path like a point in terminals
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///site.db"

# create database instance
# to create the file use terminal: from <file name> import <instance name>. Here: from app import db
# and do db.create_all()
# then import User or Post and after doing add & commit a User do for example User.query.first()
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
# this will let the login_required decorator know where the login route is.
# Argument same as in url_for this is the function where the route is located
login_manager.login_view = "login"
login_manager.login_message_category = "info"

# at the bottom to prevent circular imports
from app import routes
