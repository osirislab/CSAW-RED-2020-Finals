#!/usr/bin/env python
from flask import Flask, render_template, session, request, redirect, render_template_string
from flask_sqlalchemy import SQLAlchemy
from storage import db, Users, Pages
import os

app = Flask(__name__)
app.secret_key = b'G\x89\xaf\xa8,\xb9\xc2o\x80\xc6\x80\x9e\xab\\!i=&G\xecKn\xce\x07F\xb9\x94\x9dc\xabrH'

basedir = os.path.abspath(os.path.dirname(__file__))
SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URI') or 'sqlite:///' + os.path.join(basedir, 'app.db')

app.config['SQLALCHEMY_DATABASE_URI'] = SQLALCHEMY_DATABASE_URI
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

with app.app_context():
    db.create_all()

@app.route('/logout')
def logout():
    session.clear()
    return redirect("/")

@app.route("/", methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password'].strip()

        user = Users.query.filter_by(username=username).first()
        if user:
            if user.password == password:
                session['id'] = user.id
                return redirect("/mypages")
        
        error = "could not login"
        return render_template("index.html", error=error)

    else:
        if "id" in session:
            return redirect("/mypages")
        return render_template("index.html")


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password'].strip()

        try:
            db.session.add(Users(username=username, password=password))
            db.session.commit()
        except:
            error = "couldn't register"
            return render_template("register.html", error=error)

        user = Users.query.filter_by(username=username).first()
        session['user'] = user.id
        return redirect("/mypages")

    elif request.method == 'GET':
        return render_template("register.html")

#retrieve pages belonging to user_id
@app.route('/mypages')
def pages():
    if "id" not in session:
        return redirect("/")

    user_id = session["id"]

    page_info = []
    pages = Pages.query.filter_by(owner=user_id)
    for i in pages:
        page_info.append((i.id, i.title))

    return render_template("mypages.html", page_info=page_info)


@app.route('/create', methods=['GET', 'POST'])
def create():
    if "id" not in session:
        return redirect("/")

    if request.method == 'POST':
        user_id = session["id"]
        title = request.form['title'].strip()
        content = request.form['content'].strip()        

        page = Pages(owner=user_id, title=title, content=content)
        db.session.add(page)
        db.session.commit()

        return redirect('/mypages/' + str(page.id))

    elif request.method == 'GET':
        return render_template("create.html")


@app.route('/mypages/<id>')
def blog(id):
    if "id" not in session:
        return redirect("/")

    page = Pages.query.filter_by(id=id).first()

    if page.owner != session["id"]:
        return redirect('/mypages')

    content = render_template_string(page.content)
    return render_template("page.html", content=content, page_id=page.id, title=page.title)

@app.route('/delete/<id>')
def delete(id):
    page = Pages.query.filter_by(id=id)
    if page.owner == session["id"]:
        page.delete()
        db.session.commit()
    return redirect('/mypages')


if __name__ == "__main__":
    app.run(debug=True, threaded=True)
