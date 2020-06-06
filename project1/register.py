
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class User(db.Model):
    __tablename__ = "users"
    username = db.Column(db.String, unique=True, primary_key=True)
    password = db.Column(db.String, nullable=False)
    timeStamp = db.Column(db.DateTime, nullable=False)
