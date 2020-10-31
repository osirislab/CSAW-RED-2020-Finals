from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Users(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	username = db.Column(db.String(80), unique=True, nullable=False)
	password = db.Column(db.String(80), nullable=False)

class Pages(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	owner = db.Column(db.Integer, db.ForeignKey('users.id'))
	title = db.Column(db.String(80), nullable=False)
	content = db.Column(db.Text, nullable=False)