from flask import Flask, render_template, request, url_for, redirect, make_response, session, g
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired, Length
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
# from sqlalchemy.sql import func
import os
from flask.sessions import SecureCookieSessionInterface
from itsdangerous import URLSafeTimedSerializer
import datetime

dir_path = os.path.dirname(os.path.realpath(__file__))

app = Flask(__name__)
SECRET_KEY = "top_secret_password_dont_tell_anyone_this"
app.config['SECRET_KEY'] = SECRET_KEY

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.sqlite3'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class technologies(db.Model):
    _id = db.Column("id", db.Integer, primary_key=True)
    name = db.Column("name", db.String)
    price = db.Column("price", db.Integer)
    description = db.Column("description", db.String)
    seller = db.Column("seller", db.String)
    reviews = db.Column("reviews", db.Integer)
    def __init__(self, name, taught, description):
        self.name = name
        self.taught = taught
        self.description = description
        self.reviews = 0
        self.seller = "unknown"
class users(db.Model):
    _id = db.Column("ID", db.Integer, primary_key=True)
    username = db.Column("Username", db.String)
    realname = db.Column("Name", db.String)
    surname = db.Column("Surname", db.String)
    email = db.Column("Email", db.String)
    password = db.Column("Password", db.String)
    def __init__(self, username, realname, surname, email, password):
        self.realname = realname
        self.username = username
        self.surname = surname
        self.email = email
        self.password = password
class usercarts(db.Model):
    _id = db.Column("id", db.Integer, primary_key=True)
    userID = db.Column("userid", db.Integer, db.ForeignKey("users._id"))
    itemIDs = db.Column("itemid", db.Integer, db.ForeignKey('technologies._id'))
    amount = db.Column("amount", db.Integer)
    def __init__(self, itemIDs, userID, amount):
        self.userID = 0
        self.itemIDs = None
        self.amount = 0

with app.app_context():
    db.create_all()

class SimpleSecureCookieSessionInterface(SecureCookieSessionInterface):
	# Override method
	# Take secret_key instead of an instance of a Flask app
	def get_signing_serializer(self, secret_key):
		if not secret_key:
			return None
		signer_kwargs = dict(
			key_derivation=self.key_derivation,
			digest_method=self.digest_method
		)
		return URLSafeTimedSerializer(secret_key, salt=self.salt,
		                              serializer=self.serializer,
		                              signer_kwargs=signer_kwargs)

def decodeFlaskCookie(secret_key, cookieValue):
	sscsi = SimpleSecureCookieSessionInterface()
	signingSerializer = sscsi.get_signing_serializer(secret_key)
	return signingSerializer.loads(cookieValue)

# Keep in mind that flask uses unicode strings for the
# dictionary keys
def encodeFlaskCookie(secret_key, cookieDict):
	sscsi = SimpleSecureCookieSessionInterface()
	signingSerializer = sscsi.get_signing_serializer(secret_key)
	return signingSerializer.dumps(cookieDict)

@app.before_request
def before_request():
    session.permanent = True
    app.permanent_session_lifetime = datetime.timedelta(minutes=1440) # session will be alive for 20 minutes
    if 'userid' in session:
        user = users.query.filter_by(_id = session.get('userid')).first()
        g.user = user
    else:
        user = users.query.filter_by(_id = 0).first()
        g.user = user

class OpinionForm(FlaskForm):
    opinion = StringField('Your Opinion: ',validators = [DataRequired(),Length(min=0,max=100)])
    submit = SubmitField('Submit')

@app.route('/')
def galleryPage():
    return render_template('index.html', technologies = technologies.query.all())

@app.route('/tech/<int:techId>',methods=['GET','POST'])
def singleProductPage(techId):
    tech = db.get_or_404(technologies, techId)
    return render_template('SingleTech.html', technology = tech)

@app.route('/cart/')
def cartPage():
    usercart = usercarts.query.filter_by(userID = g.user._id)
    return render_template('cart.html', technologies = technologies.query.all(), usercart = usercart)

@app.route('/products/')
def productPage():
    return render_template('products.html', technologies = technologies.query.all())

@app.route('/references/')
def referencePage():
    return render_template('references.html')

@app.route('/gateway/', methods=['GET', 'POST'])
def loginPage():
    if request.method == 'POST':
        session.pop('userid', None)
        email = request.form['email']
        password = request.form['password']
        user = users.query.filter_by(email=email, password=password).first()
        if user:
            session['userid'] = user._id
            session_cookie = encodeFlaskCookie(SECRET_KEY, dict(session))
            return redirect(url_for('galleryPage'))
        else:
            return render_template('gateway.html') # TODO: If wrong details we need to add a message
    else:
        session['userid'] = 0
        session_cookie = encodeFlaskCookie(SECRET_KEY, dict(session))
        return render_template('gateway.html')
    
@app.errorhandler(404)
def page_not_found(error):
    return render_template('404.html', technologies = technologies.query.all(), error = error), 404

@app.errorhandler(505)
def page_not_found(error):
    return render_template('505.html', technologies = technologies.query.all(), error = error), 505
@app.errorhandler(500)
def page_not_found(error):
    return render_template('505.html', technologies = technologies.query.all(), error = error), 500

# @app.route("/logintest")
# def test():
#     session['userid'] = 1
#     session_cookie = encodeFlaskCookie(SECRET_KEY, session)
#     decodedDict = decodeFlaskCookie(SECRET_KEY, session_cookie)
#     return render_template('test.html', cookie = session_cookie, d_cookie = decodedDict, session = session.get('userid'))

@app.route('/test/')
def testPage():
    return render_template('test.html', technologies = technologies.query.all(), usercart = usercarts.query.filter_by(userID = g.user._id))

if __name__ == '__main__':
    app.run(debug=True)
