# render_template handles the html files in the template directory so not directly in script
# url_for takes care of static files like css
# flash will help with displaying text in html
# redirect: to switch route
# request: to access query parameters
import os
import secrets  # to generate random hex
from PIL import Image
from flask import render_template, url_for, flash, redirect, request, abort
from flask.scaffold import F
from app import app, db, bcrypt, mail
from app.forms import (
    RegistrationForm,
    LoginForm,
    UpdateAccountForm,
    PostForm,
    RequestResetForm,
    ResetPasswordForm,
)
from app.models import User, Post
from flask_login import login_user, current_user, logout_user, login_required
from flask_mail import Message

# route: navigating trough different site on the website
# the slash(/) is the root of the website
# stacking decorators possible
@app.route("/")
@app.route("/home")
def home():
    # query to database object Post getting all Instances of the database
    # posts = Post.query.all()

    # Arguments: 1 - key, 2 is optional - default value
    page = request.args.get("page", 1, type=int)
    # paginate created an object which has pages and each page has a limited amount of items
    # per_page means max 5 items
    posts = Post.query.order_by(Post.date_posted.desc()).paginate(page=page, per_page=5)

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
    # if user is logged in there is no need to go to register, so redirect to home
    # return statement is necessary to use redirect
    if current_user.is_authenticated:
        return redirect(url_for("home"))
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
        return redirect(url_for("login"))
    # 3rd argument pass form
    return render_template("register.html", title="Register", form=form)


@app.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("home"))
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
            return redirect(next_page) if next_page else redirect(url_for("home"))
        else:
            flash("Login Unsuccessful. Please check email and password", "danger")
    return render_template("login.html", title="Login", form=form)


@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for("home"))


def save_picture(form_picture):
    random_hex = secrets.token_hex(8)  # generate random name for uploaded file
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ext
    picture_path = os.path.join(app.root_path, "static", picture_fn)

    # delete current picture in memory
    current_picture_path = (
        User.query.filter(User.email == current_user.email).first().image_file
    )
    os.remove(os.path.join(app.root_path, "static", current_picture_path))

    # scale down picture
    output_size = (125, 125)
    i = Image.open(form_picture)
    i.thumbnail(output_size)
    i.save(picture_path)

    return picture_fn


@app.route("/account", methods=["GET", "POST"])
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
        return redirect(url_for("account"))

    # set the data for the forms to the current user data instead of being blank
    elif request.method == "GET":
        form.username.data = current_user.username
        form.email.data = current_user.email

    # url_for can also be used to find static folder & the files
    image_file = url_for("static", filename=current_user.image_file)
    return render_template(
        "account.html", title="Account", image_file=image_file, form=form
    )


@app.route("/post/new", methods=["GET", "POST"])
@login_required
def new_post():
    form = PostForm()
    if form.validate_on_submit():
        post = Post(
            title=form.title.data, content=form.content.data, author=current_user
        )
        db.session.add(post)
        db.session.commit()

        flash("Your post has been created!", "success")
        return redirect(url_for("home"))
    return render_template(
        "create_post.html", title="New Post", form=form, legend="Create Post"
    )


# using variables for route names possible
@app.route("/post/<int:post_id>")
def post(post_id):
    # instead of using get, get_or_404 also can return respectivally raises
    # raises the 404 error that the page doesent exist
    post = Post.query.get_or_404(post_id)
    return render_template("post.html", title=post.title, post=post)


@app.route("/post/<int:post_id>/update", methods=["GET", "POST"])
@login_required
def update_post(post_id):
    post = Post.query.get_or_404(post_id)
    if post.author != current_user:
        abort(403)
    # form for updating is the same as for posting
    form = PostForm()

    if form.validate_on_submit():
        post.title = form.title.data
        post.content = form.content.data
        db.session.commit()
        flash("Your post has been updated", "success")
        return redirect(url_for("post", post_id=post.id))
    elif request.method == "GET":
        form.title.data = post.title
        form.content.data = post.content
    return render_template(
        "create_post.html", title="Update Post", form=form, legend="Update Post"
    )


@app.route("/post/<int:post_id>/delete", methods=["POST"])
@login_required
def delete_post(post_id):
    post = Post.query.get_or_404(post_id)
    if post.author != current_user:
        abort(403)
    db.session.delete(post)
    db.session.commit()
    flash("Your post has been deleted", "success")
    return redirect(url_for("home"))


@app.route("/user/<string:username>")
def user_posts(username):
    page = request.args.get("page", 1, type=int)
    user = User.query.filter_by(username=username).first_or_404()
    posts = (
        Post.query.filter_by(author=user)
        .order_by(Post.date_posted.desc())
        .paginate(page=page, per_page=5)
    )
    return render_template("user_posts.html", posts=posts, user=user)


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
{url_for('reset_token', token=token, _external=True)}

If you did not make this request then simply ignore this email and no changes will be made.
"""
    mail.send(msg)


@app.route("/reset_password", methods=["GET", "POST"])
def reset_request():
    # reset request only possible if they are logged out
    if current_user.is_authenticated:
        return redirect(url_for("home"))

    form = RequestResetForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        send_reset_email(user)
        flash("An email has been sent with instructions to reset your password", "info")
        return redirect(url_for("login"))
    return render_template("reset_request.html", title="Reset Password", form=form)


@app.route("/reset_password/<token>", methods=["GET", "POST"])
def reset_token(token):
    if current_user.is_authenticated:
        return redirect(url_for("home"))

    user = User.verify_reset_token(token)
    print(token)
    print(user)
    if user is None:
        flash("That is an invalid or expired token", "warning")
        return redirect(url_for("reset_request"))

    form = ResetPasswordForm()

    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode(
            "utf-8"
        )
        user.password = hashed_password
        db.session.commit()
        flash("Your password has been updated! You are now able to log in", "success")
        return redirect(url_for("login"))
    return render_template("reset_token.html", title="Reset Password", form=form)
