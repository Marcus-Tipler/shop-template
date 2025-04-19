# ----------------------------------------------------------
# Importing all required libraries for this Flask Project.
# ----------------------------------------------------------
from flask import Flask, Blueprint, render_template, request, url_for, redirect, make_response, session, g
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from dataclasses import dataclass
from wtforms.validators import DataRequired, Length
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
import os
from flask.sessions import SecureCookieSessionInterface
from itsdangerous import URLSafeTimedSerializer
import datetime
from flask_admin import Admin
from weasyprint import HTML


# ----------------------------------------------------------
# Importing all of the assets made for this Flask Project.
# ----------------------------------------------------------
from admin.adminTechnologies import adminTechnologies # Imports templates from the Admin Folder
from admin.adminUsers import adminUsers # Imports templates from the Admin Folder
from admin.adminUsercarts import adminUsercarts # Imports templates from the Admin Folder
from context.database import db, technologies, users, usercarts # Imports blueprints from context folder.
# from context.handleCart import handleCart
from context.handleProducts import handleProductForms


# ----------------------------------------------------------
# Doing initial setup for certain aspects of the project.
# ----------------------------------------------------------
dir_path = os.path.dirname(os.path.realpath(__file__))
app = Flask(__name__)
# app.register_blueprint(handleCart)
SECRET_KEY = "top_secret_password_dont_tell_anyone_this"
app.config['SECRET_KEY'] = SECRET_KEY
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.sqlite3'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['FLASK_ADMIN_SWATCH'] = 'cerulean'

# ----------------------------------------------------------
# Initializing db from the database.py in the context folder.
# ----------------------------------------------------------
db.init_app(app)


# ----------------------------------------------------------
# Setting up Flask Admin for managing of the database.
# ----------------------------------------------------------
admin = Admin(app, name='Database Admin', template_mode='bootstrap4')
admin.add_view(adminTechnologies(technologies, db.session))
admin.add_view(adminUsers(users, db.session))
admin.add_view(adminUsercarts(usercarts, db.session))


# ----------------------------------------------------------
# Create databases if none exist.
# ----------------------------------------------------------
with app.app_context():
    db.create_all()


# ----------------------------------------------------------
# Initializing Cookie Serializer for the session.
# ----------------------------------------------------------
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
# Keep in mind that flask uses unicode strings for the dictionary keys
def encodeFlaskCookie(secret_key, cookieDict):
	sscsi = SimpleSecureCookieSessionInterface()
	signingSerializer = sscsi.get_signing_serializer(secret_key)
	return signingSerializer.dumps(cookieDict)


# ----------------------------------------------------------
# Initializing initial account cookies for the user.
# ----------------------------------------------------------
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


# ----------------------------------------------------------
# Root initializations for the Flask Project.
# ----------------------------------------------------------
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

@app.route('/products/', methods=['GET', 'POST'])
def productPage():
    form = handleProductForms()
    form.choices.choices = [(tech._id, tech.name) for tech in technologies.query.all()]
    for tech in technologies.query.all():
        print(tech._id, tech.name)
    print('\n')
    if request.method == 'POST':
    # if form.validate_on_submit():
        selected_technologies = request.form.getlist('choices')
        selected_technologies = [int(tech_id) for tech_id in selected_technologies] # Get the ID values from the form
        env_impact_threshold = form.env_impact.data # Get the slider value for environmental impact
        selected_technologies = technologies.query.filter(
            technologies._id.in_(selected_technologies),
            technologies.env_impact <= env_impact_threshold
        ).all()
        for tech in selected_technologies:
            print(tech)
        return render_template('products.html', technologies = selected_technologies, form = form)
    return render_template('products.html', technologies = technologies.query.all(), form = form)

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


# ----------------------------------------------------------
# Error handling for Catastrophic fails on the Flask Project.
# ----------------------------------------------------------
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


# @app.route('/test/')
# def testPage():
#     return render_template('test.html', technologies = technologies.query.all(), usercart = usercarts.query.filter_by(userID = g.user._id))


# ----------------------------------------------------------
# Creates parameters for the application to run.
# ----------------------------------------------------------
if __name__ == '__main__':
	app.run(
          debug=True,
          host='0.0.0.0',
          port=5000
          )
