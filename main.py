from flask import Flask, render_template, session, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from werkzeug.utils import secure_filename
from datetime import datetime
import random
import pymysql
import os
import json

with open('config.json', 'r') as c:
    params = json.load(c)["params"]

app = Flask(__name__)
app.secret_key = "secret-key"
app.config['SQLALCHEMY_DATABASE_URI'] = "mysql://root:@localhost/coltdlistdb1804"
app.config['UPLOAD_FOLDER'] = params['path']
app.config['AVATAR_FOLDER'] = params['avtr']
db = SQLAlchemy(app) 
con = pymysql.connect(host='localhost', user='root', password='', database='coltdlistdb1804')


class Users(db.Model):
    username = db.Column(db.String(20), unique=True, nullable=False, primary_key=True)
    email = db.Column(db.String(50), unique=True, nullable=False, primary_key=True)
    password = db.Column(db.String(30), unique=False, nullable=False, primary_key=True)
    contact = db.Column(db.String(20), unique=True, nullable=False, primary_key=True)


class Blogs(db.Model):
    username = db.Column(db.String(20), unique=False, nullable=False, primary_key=True)
    thumbnail = db.Column(db.String(600), unique=False, nullable=False, primary_key=True)
    title = db.Column(db.String(120), unique=False, nullable=False, primary_key=True)
    category = db.Column(db.String(100), unique=False, nullable=False, primary_key=True)
    blog = db.Column(db.String(1200), unique=False, nullable=False, primary_key=True)
    link = db.Column(db.String(100), unique=True, nullable=False, primary_key=True)
    date = db.Column(db.String(50), unique=True, nullable=False, primary_key=True)


class Appear(db.Model):
    username = db.Column(db.String(20), unique=False, nullable=False, primary_key=True)
    dark = db.Column(db.String(20), unique=False, nullable=False, primary_key=True)
    avatar = db.Column(db.String(700), unique=True, nullable=False, primary_key=True)

class Files(db.Model):
    filename = db.Column(db.String(600), unique=False, nullable=False, primary_key=True)


class Avatar(db.Model):
    avatar = db.Column(db.String(700), unique=False, nullable=False, primary_key=True)

class Searched(db.Model):
    username = db.Column(db.String(100), unique=False, nullable=False, primary_key=True)
    search = db.Column(db.String(500), unique=False, nullable=False, primary_key=True)


@app.route("/", methods=['GET', 'POST'])
def home():
    try:
        username=session['username']
    except:
        username="Guest"
    categ = ['Lifestyle', 'Music', 'Gaming', 'Management', 'Health', 'Food']
    category = random.choice(categ)
    tle = Searched.query.filter_by(username=username).first()
    posts = Blogs.query.filter_by(category=category).all()[0:5]
    post1 = Blogs.query.filter_by(username=username).first()
    post2 = Blogs.query.filter_by(category=category).first()
    post3 = Blogs.query.filter_by(username=tle.search).first()

    if (request.method=='POST'):
        try:
            username = session['username']
        except:
            username = "Guest"
        search = request.form.get("query")
        try:
            srch = Searched.query.filter_by(username=username).first()
            srch.username = username
            srch.search = search
            db.session.add(srch)
            db.session.commit()
        except:
            data = Searched(username=username, search=search)
            db.session.add(data)
            db.session.commit()
        return redirect(url_for("search"))

    if 'username' in session:
        username=session['username']
        post = Users.query.filter_by(username=username).first()
        theme = Appear.query.filter_by(username=username).first()
        return render_template("home.html", username=session['username'], posts=posts,  theme=theme, post=post, post3=post3, post2=post2, post1=post1)
    
    return render_template("home.html", posts=posts,  post3=post3, post2=post2, post1=post1)
    

@app.route("/blog/<string:link>", methods=['GET'])
def blogs(link):
    post = Blogs.query.filter_by(link=link).first()
    return render_template("blog.html", post=post)

@app.route("/signup", methods= ['GET', 'POST'])
def signup():
    if (request.method=='POST'):
        username = request.form.get("username")
        email = request.form.get("email")
        password = request.form.get("password")
        contact = request.form.get("contact")

        dark = 0
        avatar = "user.jpg"

        search = username

        data = Appear(username=username, dark=dark, avatar=avatar)
        db.session.add(data)
        db.session.commit()

        data = Users(username=username, email=email, password=password, contact=contact)
        db.session.add(data)
        db.session.commit()

        data = Searched(username=username, search=search)
        db.session.add(data)
        db.session.commit()
        
    return render_template("signup.html")


@app.route("/login", methods= ['GET', 'POST'])
def login():
    if (request.method == 'POST'):
        username = request.form["username"]
        pwd = request.form["password"]
        cur = con.cursor()
        cur.execute(f"select username, password from users where username = '{username}'")
        user = cur.fetchone()
        cur.close()
        if user and pwd == user[1]:
            session['username'] = user[0]
            return redirect(url_for("home"))
        else:
            return render_template("login.html", error='Invalid Email or Password')
    return render_template("login.html")

@app.route("/create-blog", methods= ['GET', 'POST'])
def createBlog():
    if (request.method=='POST'):
        chars = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890"
        length=8
        link="".join(random.sample(chars, length))

        username = session['username']
        thumbnail = request.form.get("img")
        title = request.form.get("title")
        category = request.form.get("category")
        blog = request.form.get("blog")

        data = Blogs(username=username, thumbnail=thumbnail, title=title, link=link, category=category, blog=blog, date=datetime.now())
        db.session.add(data)
        db.session.commit()
        return render_template("cr-blog.html")

    return render_template("create-blog.html")

@app.route("/cr-blog", methods= ['GET', 'POST'])
def crBlog():
    if (request.method=='POST'):
        filename = request.files["img"]

        file = Files(filename=filename)
        db.session.add(file)
        db.session.commit()
        
        filename.save(os.path.join(app.config['UPLOAD_FOLDER'], secure_filename(filename.filename)))
        return redirect(url_for("home"))

    return render_template("cr-blog.html")

@app.route("/user/<string:email>", methods= ['GET', 'POST'])
def user(email):
    if (request.method=='POST'):
        e_mail = request.form.get("email")
        contact = request.form.get("contact")
        password = request.form.get("password")
        info = Users.query.filter_by(e_mail=email).first()
        info.email = e_mail
        info.conatct = contact
        info.password = password
        db.session.add(info)
        db.session.commit()

    return render_template("user.html", username=session['username'])

@app.route("/settings", methods= ['GET', 'POST'])
def settings():
    username = session['username']
    info = Users.query.filter_by(username=username).first()
    return render_template("settings.html", username=session['username'], info=info)

@app.route("/profile", methods= ['GET', 'POST'])
def profile():
    username = session['username']

    if (request.method == 'POST'):
        username = session['username']
        dark = request.form.get("dark")
        avatar = request.form.get("img")
        ost = Appear.query.filter_by(username=username).first()

        ost.dark = dark
        ost.avatar = avatar
        db.session.add(ost)
        db.session.commit()
        return redirect(url_for("home"))

    return render_template("profile.html")


@app.route("/user", methods= ['GET', 'POST'])
def pr():
    if (request.method=='POST'):
        avatar = request.files["avtr"]

        file = Avatar(avatar=avatar)
        db.session.add(file)
        db.session.commit()
        
        avatar.save(os.path.join(app.config['AVATAR_FOLDER'], secure_filename(avatar.filename)))
        return redirect(url_for("home"))
    
    return render_template("pr.html")


@app.route("/<string:link>/edit", methods= ['GET', 'POST'])
def editBlog(link):
    data1 = Blogs.query.filter_by(link=link).first()
    if (request.method == 'POST'):
        img = request.form.get("img")
        title = request.form.get("title")
        category = request.form.get("category")
        blog = request.form.get("blog")
        ost = Blogs.query.filter_by(link=link).first()

        ost.thumbnail = img
        ost.title = title
        ost.category = category
        ost.blog = blog
        db.session.add(ost)
        db.session.commit()

    return render_template("edit-blog.html", info=data1)


@app.route("/logout")
def logout():
    session.pop('username', None)
    return redirect(url_for('home'))

@app.route("/searched-for", methods= ['GET', 'POST'])
def search():
    try:
        username = session['username']
    except:
        username = "Guest"
    searched = Searched.query.filter_by(username=username).first()

    link = Blogs.query.filter_by(link=searched.search).all()[0:5]
    title = Blogs.query.filter_by(title=searched.search).all()[0:5]
    user = Users.query.filter_by(username=searched.search).all()[0:3]
    userBlog = Blogs.query.filter_by(username=searched.search).all()[0:5]
    category = Blogs.query.filter_by(category=searched.search).all()[0:100]
    return render_template("search.html", search=searched, title=title, url=link, user=user, category=category, userBlog=userBlog)


@app.route("/<string:account>", methods= ['GET', 'POST'])
def account(account):
    user = Users.query.filter_by(username=account).first()
    logo = Appear.query.filter_by(username=account).first()
    return render_template("accounts.html", user=user, logo=logo)


app.run(debug=True)