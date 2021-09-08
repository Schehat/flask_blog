from datetime import datetime
from app import db, login_manager
from flask_login import UserMixin


@login_manager.user_loader
def load_user(user_id):
    # return user by user_id from database
    return User.query.get(int(user_id))


# those models User & Post have later access to the database and can perform queries
# db.Model takes care of databas related stuff & UserMixin is for easy login
class User(db.Model, UserMixin):
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
