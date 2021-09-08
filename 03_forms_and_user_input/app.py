# render_template handles the html files in the template directory so not directly in script
# url_for takes care of static files like css
# flash will help with displaying text in html
# redirect: to switch route
from flask import Flask, render_template, url_for, flash, redirect
from forms import RegistrationForm, LoginForm

# __name__ will equal __main__ and this for flask to know where
# to look for templates & static files and so on
app = Flask(__name__)

# for security meseaures. Random set of character
app.config["SECRET_KEY"] = "c199a4bd65fd34f90e38674dde8f8703"

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
