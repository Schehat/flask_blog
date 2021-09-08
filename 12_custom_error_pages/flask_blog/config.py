import os


class Config:
    # for security meseaures to prevent CSRF attacks. Set of random character
    SECRET_KEY = "c199a4bd65fd34f90e38674dde8f8703"
    # set location of database. Triple slash(///) is for relative path like a point in terminals
    SQLALCHEMY_DATABASE_URI = "sqlite:///site.db"
    MAIL_SERVER = "smtp-mail.outlook.com"
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USE_SSL = False
    MAIL_USERNAME = "flask_blog_reset@outlook.de"
    MAIL_PASSWORD = os.environ.get("flask_blog_reset_password")
