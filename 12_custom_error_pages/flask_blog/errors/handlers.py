from flask import Blueprint, render_template

errors = Blueprint("errors", __name__)


# creating a error handler is simalair to creating a route, but with a different decorator
# Errorhandler should be used for the entire application, thus using app_errorhander
# To only work in this blueprint errorhandler is the way to go
@errors.app_errorhandler(404)
def error_404(error):
    # 2nd argument: status code. In routes not necessary because default is 200 which means ok
    # 404 means ressource not available
    return render_template("errors/404.html"), 404


# 403 means the server understood the request but refuses to allow it
@errors.app_errorhandler(403)
def error_403(error):
    return render_template("errors/403.html"), 403


# 500 means could not not handle request due to unexpected circumstances.It is for catching all errors
@errors.app_errorhandler(500)
def error_500(error):
    return render_template("errors/500.html"), 500
