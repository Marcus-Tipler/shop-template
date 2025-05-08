from flask import Flask, render_template, request, url_for, redirect, make_response, session, g
from flask_sqlalchemy import SQLAlchemy
from dataclasses import dataclass
# from flask_admin import Admin

db = SQLAlchemy()

@dataclass
class technologies(db.Model):
    __tablename__ = 'technologies'
    _id = int
    name = str
    price = int
    description = str
    seller_id = str
    reviews = int
    env_impact = int

    _id = db.Column("id", db.Integer, primary_key=True)
    name = db.Column("name", db.String(255))
    price = db.Column("price", db.Integer)
    description = db.Column("description", db.Text)
    reviews = db.Column("reviews", db.Integer)
    env_impact = db.Column("env_impact", db.Integer)

    seller_id = db.Column("seller_id", db.ForeignKey("sellers.id"), nullable=False)
    seller = db.relationship("sellers", backref=db.backref("technologies", lazy=True))

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
class sellers(db.Model):
    __tablename__ = 'sellers'
    _id = int
    seller_name = str

    _id = db.Column("id", db.Integer, primary_key=True)
    seller_name = db.Column("seller_name", db.String(255))

    def __str__(self):
        return f"{self.seller_name}"


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
    

@dataclass
class userAddress(db.Model):
    __tablename__ = 'userAddress'
    _id = int
    userID = int
    phone = str
    postcode = str
    address_line1 = str
    city = str
    country = str
    state = str

    _id = db.Column("id", db.Integer, primary_key=True, autoincrement=True)
    phone = db.Column("phone", db.String(20), nullable=True)
    postcode = db.Column("postcode", db.String(20), nullable=False)
    address_line1 = db.Column("address_line1", db.String(255), nullable=False)
    city = db.Column("city", db.String(100), nullable=False)
    country = db.Column("country", db.String(100), nullable=False)
    state = db.Column("state", db.String(100), nullable=True)

    userID = db.Column("userid", db.Integer, db.ForeignKey("users.ID"), nullable=False)
    user = db.relationship("users", backref=db.backref("userAddress", lazy=True))

    def __str__(self):
        return f"{self.address_line1}, {self.city}, {self.state}, {self.country}, {self.postcode}, {self.phone}"


@dataclass
class userBanking(db.Model):
    __tablename__ = 'userBanking'
    _id = int
    userID = int
    cardholder_name = str
    card_number = str
    cvv = str
    expiry_date = str
    billing_address_id = int

    _id = db.Column("id", db.Integer, primary_key=True, autoincrement=True)
    cardholder_name = db.Column("cardholder_name", db.String(255), nullable=False)
    card_number = db.Column("card_number", db.String(16), nullable=False)
    cvv = db.Column("cvv", db.String(4), nullable=False)
    expiry_date = db.Column("expiry_date", db.String(7), nullable=False)  # Format: MM/YYYY

    userID = db.Column("userid", db.Integer, db.ForeignKey("users.ID"), nullable=False)
    user = db.relationship("users", backref=db.backref("userBanking", lazy=True))
    billing_address_id = db.Column("billing_address_id", db.Integer, db.ForeignKey("userAddress.id"), nullable=False)
    billing_address = db.relationship("userAddress", backref=db.backref("userBanking", lazy=True))

    def __str__(self):
        return f"Cardholder: {self.cardholder_name}, Card: **** **** **** {self.card_number[-4:]}, Expiry: {self.expiry_date}"