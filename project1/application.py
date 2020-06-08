import os
import time
import requests
from flask import Flask, session, render_template, request, redirect, url_for
from register import *
from sqlalchemy import or_

app = Flask(__name__)


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
    return "Project 1: TODO"


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
