# render_template handles the html files in the template directory so not directly in script
# url_for takes care of static files like css
# flash will help with displaying text in html
# redirect: to switch route
from datetime import datetime
from flask import Flask, render_template, url_for, flash, redirect
from flask_sqlalchemy import SQLAlchemy
from forms import RegistrationForm, LoginForm

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


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    # argument 20 is the max length like specified in forms
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    image_file = db.Column(db.String(20), nullable=False, default="default.jpg")
    password = db.Column(db.String(60), nullable=False)

    # arguments: 1. has relationship with Post model
    # 2. backref is similar to adding a new column in Post model & can access the attribute
    # in dot notation <Post instance>.author returns the user instance for this post
    # 3. lazy means sqlalchemy will load the data completely if necessary
    posts = db.relationship("Post", backref="author", lazy=True)

    def __repr__(self):
        return f"User('{self.username}', '{self.email}', '{self.image_file}')"


class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    # Note: default pass the function and not the current time, thus no paranthesis
    # for databases utcnow is recommended instead of today due utcnow has universal time zone
    date_posted = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    content = db.Column(db.Text, nullable=False)

    # db.ForeignKey: lowercase due to not reffering to the class User but the table & column
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)

    def __repr__(self):
        return f"Post('{self.title}', '{self.date_posted}')"


# dummy data
posts = [
    {
        "author": "Corey Schafer",
        "title": "Blog Post 1",
        "content": "First post content",
        "date_posted": "April 20, 2018",
    },
    {
        "author": "Jane Doe",
        "title": "Blog Post 2",
        "content": "Second post content",
        "date_posted": "April 21, 2018",
    },
]

# route: navigating trough different site on the website
# the slash(/) is the root of the website
# stacking decorators possible
@app.route("/")
@app.route("/home")
def home():
    # instead of typing here all html
    # can use any argument e.g. posts and this parameter will be a variable
    # in the html file
    return render_template("home.html", posts=posts)


@app.route("/about")
def about():
    return render_template("about.html", title="About")


# 2nd argument methods: allows which request this route can handle
@app.route("/register", methods=["GET", "POST"])
def register():
    form = RegistrationForm()
    # check if submit was entered
    if form.validate_on_submit():
        # flash: easy way to display a message
        # 2nd argument is for Bootstrap classes what kind of message it should be
        flash(f"Account created for {form.username.data}!", "success")
        # redirect to different route. url_for takes as a argument the name of the function
        # for this route. Not the name of the route!
        return redirect(url_for("home"))
    # 3rd argument pass form
    return render_template("register.html", title="Register", form=form)


@app.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        # simulate login with fake data
        if form.email.data == "admin@blog.com" and form.password.data == "password":
            flash("You have been logged in!", "success")
            return redirect(url_for("home"))
        else:
            flash("Login Unsuccessful. Please check email and password", "danger")
    return render_template("login.html", title="Login", form=form)


if __name__ == "__main__":
    app.run(debug=True)
