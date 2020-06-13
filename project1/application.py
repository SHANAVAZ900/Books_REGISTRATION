import os
import time
import requests
from flask import Flask, json, redirect, render_template, request, session, url_for
from register import *
from sqlalchemy import or_
from booklist import books


app = Flask(__name__)
app.secret_key = 'my precious'


# Check for environment variable
if not os.getenv("DATABASE_URL"):
    raise RuntimeError("DATABASE_URL is not set")

# Configure session to use filesystem
app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db.init_app(app)

with app.app_context():
    db.create_all()


@app.route("/")
def index():
    return render_template('registration.html')


@app.route("/admin")
def allusers():
    users = User.query.all()
    return render_template('admin.html', users=users)


@app.route("/register", methods=["GET", "POST"])
def userDetails():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        # checking the user data is present or not
        userData = User.query.filter_by(username=username).first()

        if userData is not None:
            return render_template("registration.html", message="email already exists, Please login.")
        else:
            user = User(
                username=username, password=password, timeStamp=time.ctime(time.time()))

            # checking the registration details entered perfectly or not
            try:
                db.session.add(user)
                db.session.commit()
                return render_template("home.html",  username=username, message="Successfully entered")

            except:
                return render_template("registration.html", message="please fill the details properly")
    return render_template("registration.html")


@app.route("/home/<user>")
def userHome(user):
    if user in session:
        return render_template("search.html", username=user, message="entered successful")
    return redirect(url_for('index'))


@app.route("/auth", methods=["POST", "GET"])
def auth():
    if request.method == "POST":
        username = request.form.get('username')
        password = request.form.get('password')

        # checking if the user is there or not
        userData = User.query.filter_by(username=username).first()

        # if the user is there then checking username and password is correct
        if userData is not None:
            if userData.username == username and userData.password == password:
                session[username] = username
                return redirect(url_for("userHome", user=username))
            # user verification failed
            else:
                return render_template("registration.html", message="username/password is incorrect!!")
        else:
            return render_template("registration.html", message="Account doesn't exists, Please register!")


@app.route("/logout/<username>", methods=["POST", "GET"])
def logout(username):
    session.pop(username, None)
    return render_template("registration.html", message="logged out successful")


@app.route("/search/<username>", methods=["POST", "GET"])
def search(username):

    if request.method == "GET":
        return redirect(url_for('index'))

    else:
        res = request.form.get("find")
        res = '%'+res+'%'
        result = books.query.filter(or_(books.title.ilike(
            res), books.author.ilike(res), books.isbn.ilike(res))).all()
        return render_template("search.html", result=result, username=username)


@app.route("/bookpage/<username>/<isbn>", methods=["POST", "GET"])
def bookpage(username, isbn):

    user1 = username
    bookisbn = isbn
    # allow the user only if he in session
    if user1 in session:
        # details are being retrieved from goodreads api
        res = requests.get("https://www.goodreads.com/book/review_counts.json",
                           params={"key": "GfoQsiFrU8JgChm0fDRMA", "isbns": bookisbn})

        book = books.query.filter_by(isbn=bookisbn).first()
        # Parsing the data
        data = res.text
        parsed = json.loads(data)
        print(parsed)
        res = {}
        for i in parsed:
            for j in (parsed[i]):
                res = j

        return render_template("bookpage.html", book=book, res=res,  username=user1)

    else:
        return redirect(url_for('index'))
