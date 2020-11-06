from flask import Flask, render_template, abort
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, current_user

import config  # noqa: F401

app = Flask(__name__, template_folder='template', static_folder='static')
app.config.from_object('config.Prod')
login = LoginManager(app)
db = SQLAlchemy(app)


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False, unique=True)


class Album(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    creator_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    creator = db.relationship('User', backref='albums', lazy=True)
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text, nullable=False, default="")
    draft = db.Column(db.Boolean, nullable=False, default=True)


class Photo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    album_id = db.Column(db.Integer, db.ForeignKey('album.id'), nullable=False)
    album = db.relationship('Album', backref=db.backref('photos', lazy=False))
    url = db.Column(db.String(4095), nullable=False)
    description = db.Column(db.Text, nullable=False, default="")


db.create_all()


@login.user_loader
def load_user(id):
    return User.query.get(int(id))


# TODO: user registration


@app.route("/")
def index():
    if current_user.is_authenticated:
        return render_template('index.html', albums=Album.query.all())
    else:
        return render_template('index.html', albums=Album.query.filter(Album.draft == False).all())


@app.route("/album/<int:album_id>")
def album(album_id):
    album = Album.query.get_or_404(album_id)
    if album.draft and not current_user.is_authenticated:
        abort(403)

    return render_template('album.html', album=album)


@app.route("/resize")
def resize():
    # Due to overwhelming demand, this is now on a separate container than can be scaled independently.
    # This is just kept here to make url_for clean
    return 'This should be unreachable'


if __name__ == "__main__":
    app.run(port=8000)
