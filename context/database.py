from flask import Flask, render_template, request, url_for, redirect, make_response, session, g
from flask_sqlalchemy import SQLAlchemy
from dataclasses import dataclass
from flask_admin import Admin

db = SQLAlchemy()

@dataclass
class technologies(db.Model):
    __tablename__ = 'technologies'
    _id = int
    name = str
    price = int
    description = str
    seller = str
    reviews = int

    _id = db.Column("id", db.Integer, primary_key=True)
    name = db.Column("name", db.String(255))
    price = db.Column("price", db.Integer)
    description = db.Column("description", db.Text)
    seller = db.Column("seller", db.String(255))
    reviews = db.Column("reviews", db.Integer)

    def __str__(self):
        return f"{self.name} / {self.price} / {self.description} / {self.seller} / {self.reviews}"
    

@dataclass
class users(db.Model):
    __tablename__ = 'users'
    _id = int
    username = str
    realname = str
    surname = str
    email = str
    password = str

    _id = db.Column("ID", db.Integer, primary_key=True)
    username = db.Column("Username", db.String(255))
    realname = db.Column("Name", db.String(255))
    surname = db.Column("Surname", db.String(255))
    email = db.Column("Email", db.String(255))
    password = db.Column("Password", db.Text)

    def __str__(self):
        return f"{self.username} / {self.realname} / {self.surname} / {self.email} / {self.password}"


@dataclass
class usercarts(db.Model):
    __tablename__ = 'usercarts'
    _id = int
    userID = int
    itemIDs = int
    amount = int

    _id = db.Column("id", db.Integer, primary_key=True)
    amount = db.Column("amount", db.Integer)

    userID = db.Column("userid", db.Integer, db.ForeignKey("users.ID"), nullable=False)
    user = db.relationship("users", backref=db.backref("usercarts", lazy=True))
    itemIDs = db.Column("itemid", db.Integer, db.ForeignKey('technologies.id'), nullable=False)
    item = db.relationship("technologies", backref=db.backref("usercarts", lazy=True))

    def __str__(self):
        return f"{self.amount}"