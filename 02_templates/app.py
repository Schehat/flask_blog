# render_template handles the html files in the template directory so not directly in script
# url_for takes care of static files like css
from flask import Flask, render_template, url_for

# __name__ will equal __main__ and this for flask to know where
# to look for templates & static files and so on
app = Flask(__name__)

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


if __name__ == "__main__":
    app.run(debug=True)
