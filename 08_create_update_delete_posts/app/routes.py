# render_template handles the html files in the template directory so not directly in script
# url_for takes care of static files like css
# flash will help with displaying text in html
# redirect: to switch route
# request: to access query parameters
import os
import secrets  # to generate random hex
from PIL import Image
from flask import render_template, url_for, flash, redirect, request, abort
from app import app, db, bcrypt
from app.forms import RegistrationForm, LoginForm, UpdateAccountForm, PostForm
from app.models import User, Post
from flask_login import login_user, current_user, logout_user, login_required

# route: navigating trough different site on the website
# the slash(/) is the root of the website
# stacking decorators possible
@app.route("/")
@app.route("/home")
def home():
    # query to database object Post getting all Instances of the database
    posts = Post.query.all()
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
