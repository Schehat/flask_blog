from flask import Flask

# __name__ will equal __main__ and this for flask to know where
# to look for templates & static files and so on
app = Flask(__name__)

# route: navigating trough different site on the website
# the slash(/) is the root of the website
# the function usually returns a html file but in this case
# just print a string
@app.route("/")
def hello():
    return "<h1>hello world!</h1>"


if __name__ == "__main__":
    # with debug mode changes will be loaded automatically
    app.run(debug=True)

# instead of the if statement this works too to run app:
# file name has to be app.py to work, for me at least. In general name not restricted
# in terminal (windows): set FLASK_APP=app.py
#                        optional: set FLASK_DEBUG=1 => this doesent work for me either...
#                        flask run
# output: http://127.0.0.1:5000, local ip address & port to open website locally
# replacing 127.0.0.1 with localhost possible
