from flask import Flask, render_template, url_for, flash, redirect
from flask_sqlalchemy import SQLAlchemy

# __name__ will equal __main__ and this for flask to know where
# to look for templates & static files and so on
app = Flask(__name__)
# for security meseaures. Random set of character
app.config["SECRET_KEY"] = "c199a4bd65fd34f90e38674dde8f8703"
# set location of database. Triple slash(///) is for relative path like a point in terminals
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///site.db"

# create database instance
# to create the file use terminal: from <file name> import <instance name>. Here: from app import db
# and do db.create_al()
db = SQLAlchemy(app)

# at the bottom to prevent circular imports
from app import routes
