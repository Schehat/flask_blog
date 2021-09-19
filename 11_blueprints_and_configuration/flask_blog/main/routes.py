# render_template handles the html files in the template directory so not directly in script
# request: to access query parameters
from flask import Blueprint, render_template, request
from flask_blog.models import Post

main = Blueprint("main", __name__)


# route: navigating trough different site on the website
# the slash(/) is the root of the website
# stacking decorators possible
@main.route("/")
@main.route("/home")
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


@main.route("/about")
def about():
    return render_template("about.html", title="About")
