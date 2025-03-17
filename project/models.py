from datetime import datetime
from flask_login import UserMixin
from . import db

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)  # Primary keys sind erforderlich
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100))
    name = db.Column(db.String(1000))

    posts = db.relationship('Post', backref='user', lazy=True)
    comments = db.relationship('Comment', backref='comment_author', lazy=True)

class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    meinung = db.Column(db.Text, nullable=False)
    book_author = db.Column(db.String(255))
    isbn = db.Column(db.String(50))
    published_date = db.Column(db.String(50))
    image = db.Column(db.String(255))  # Neues Feld für die Bild-URL
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    date_created = db.Column(db.DateTime, default=datetime.utcnow)
    comments = db.relationship('Comment', backref='post', lazy=True, cascade="all, delete-orphan")


class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.Text, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'), nullable=False)
    # Datum und Uhrzeit, zu der der Kommentar erstellt wurde:
    date_created = db.Column(db.DateTime, default=datetime.utcnow)