# url_for takes care of static files like css
# flash will help with displaying text in html
# redirect: to switch route
from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_blog import bcrypt, db
from flask_blog.models import Post, User
from flask_blog.users.forms import (
    LoginForm,
    RegistrationForm,
    RequestResetForm,
    ResetPasswordForm,
    UpdateAccountForm,
)
from flask_blog.users.utils import save_picture, send_reset_email
from flask_login import current_user, login_required, login_user, logout_user

# arguments: name of the blueprint, ...
users = Blueprint("users", __name__)


@users.route("/register", methods=["GET", "POST"])
def register():
    # if user is logged in there is no need to go to register, so redirect to home
    # return statement is necessary to use redirect
    if current_user.is_authenticated:
        return redirect(url_for("main.home"))
    form = RegistrationForm()
    # check if submit was entered & fulfills validation requirements
    if form.validate_on_submit():
        # decode at the end to get a hashed-string
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode(
            "utf-8"
        )
        user = User(
            username=form.username.data, email=form.email.data, password=hashed_password
        )

        # add user to the database & commit it
        db.session.add(user)
        db.session.commit()

        # flash: easy way to display a message
        # 2nd argument is for Bootstrap classes what kind of message it should be
        flash("Your account has been created! You are now able to log in", "success")
        # redirect to different route. url_for takes as a argument the name of the function
        # for this route. Not the name of the route!
        return redirect(url_for("users.login"))
    # 3rd argument pass form
    return render_template("register.html", title="Register", form=form)


@users.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("main.home"))
    form = LoginForm()
    if form.validate_on_submit():
        # queries form sqlalchemy do not need dot notation but forms do
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            # if user entered in url account but was not logged and then logs in
            # this will make to get the query parameter which to go next, here account and
            # not redirect to home
            # Note: args is a dictionary but access with brackets is not good due to if
            # key does not exist it will throw an error. But with get it will return None
            next_page = request.args.get("next")
            # next_page includes the route for the next page, so can pass it like this
            return redirect(next_page) if next_page else redirect(url_for("main.home"))
        else:
            flash("Login Unsuccessful. Please check email and password", "danger")
    return render_template("login.html", title="Login", form=form)


@users.route("/logout")
def logout():
    logout_user()
    return redirect(url_for("main.home"))


@users.route("/account", methods=["GET", "POST"])
# with this decorator only if logged in this route can be accessed
@login_required
def account():
    form = UpdateAccountForm()
    if form.validate_on_submit():
        if form.picture.data:
            picture_file = save_picture(form.picture.data)
            current_user.image_file = picture_file
        current_user.username = form.username.data
        current_user.email = form.email.data
        db.session.commit()
        flash("Your account has been updated!", "success")
        return redirect(url_for("users.account"))

    # set the data for the forms to the current user data instead of being blank
    elif request.method == "GET":
        form.username.data = current_user.username
        form.email.data = current_user.email

    # url_for can also be used to find static folder & the files
    image_file = url_for("static", filename=current_user.image_file)
    return render_template(
        "account.html", title="Account", image_file=image_file, form=form
    )


@users.route("/user/<string:username>")
def user_posts(username):
    page = request.args.get("page", 1, type=int)
    user = User.query.filter_by(username=username).first_or_404()
    posts = (
        Post.query.filter_by(author=user)
        .order_by(Post.date_posted.desc())
        .paginate(page=page, per_page=5)
    )
    return render_template("user_posts.html", posts=posts, user=user)


@users.route("/reset_password", methods=["GET", "POST"])
def reset_request():
    # reset request only possible if they are logged out
    if current_user.is_authenticated:
        return redirect(url_for("main.home"))

    form = RequestResetForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        send_reset_email(user)
        flash("An email has been sent with instructions to reset your password", "info")
        return redirect(url_for("users.login"))
    return render_template("reset_request.html", title="Reset Password", form=form)


@users.route("/reset_password/<token>", methods=["GET", "POST"])
def reset_token(token):
    if current_user.is_authenticated:
        return redirect(url_for("main.home"))

    user = User.verify_reset_token(token)
    print(token)
    print(user)
    if user is None:
        flash("That is an invalid or expired token", "warning")
        return redirect(url_for("users.reset_request"))

    form = ResetPasswordForm()

    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode(
            "utf-8"
        )
        user.password = hashed_password
        db.session.commit()
        flash("Your password has been updated! You are now able to log in", "success")
        return redirect(url_for("users.login"))
    return render_template("reset_token.html", title="Reset Password", form=form)
