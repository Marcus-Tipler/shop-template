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
# from flask_admin import Admin
# from weasyprint import HTML


# ----------------------------------------------------------
# Importing all of the assets made for this Flask Project.
# ----------------------------------------------------------
# from admin.adminTechnologies import adminTechnologies # Imports templates from the Admin Folder
# from admin.adminUsers import adminUsers # Imports templates from the Admin Folder
# from admin.adminUsercarts import adminUsercarts # Imports templates from the Admin Folder
from context.database import db, technologies, users, usercarts, sellers # Imports blueprints from context folder.
# from context.handleCart import handleCart
from context.handleProducts import handleProductForms
from context.handleCart import updateCartCookie, modifyCart # Imports blueprints from context folder.


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
# app.config['FLASK_ADMIN_SWATCH'] = 'cerulean'

# ----------------------------------------------------------
# Initializing db from the database.py in the context folder.
# ----------------------------------------------------------
db.init_app(app)


# ----------------------------------------------------------
# Setting up Flask Admin for managing of the database.
# ----------------------------------------------------------
# admin = Admin(app, name='Database Admin', template_mode='bootstrap4')
# admin.add_view(adminTechnologies(technologies, db.session))
# admin.add_view(adminUsers(users, db.session))
# admin.add_view(adminUsercarts(usercarts, db.session))


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

    # Initialize cart in session if it doesn't exist
    if 'cart' not in session:
        session['cart'] = {}  # Initialize as an empty dictionary

class OpinionForm(FlaskForm):
    opinion = StringField('Your Opinion: ',validators = [DataRequired(),Length(min=0,max=100)])
    submit = SubmitField('Submit')


# ----------------------------------------------------------
# Root initializations for the Flask Project.
# ----------------------------------------------------------
@app.route('/')
def galleryPage():
    return render_template('index.html', technologies = technologies.query.limit(3).all())

@app.route('/tech/<int:techId>',methods=['GET','POST'])
def singleProductPage(techId):
    tech = db.get_or_404(technologies, techId)
    print(tech)
    return render_template('SingleTech.html', technology = tech)

@app.route('/cart/')
def cartPage():
    # Load the cart from the session
    cart, totalCost = updateCartCookie(g.user, usercarts, session, db, technologies)  # Update the cart in the session with the database
    session_cart = session.get('cart', {})  # Get the cart from the session, default to an empty dictionary
    usercart = usercarts.query.filter_by(userID = g.user._id)
    totalItems = len(usercart.all())
    # Process the cart to fetch item details from the database
    cart_items = []
    total_cost = 0
    total_items = 0
    for item_id_str, quantity in session_cart.items():
        item_id = int(item_id_str)
        item = technologies.query.filter_by(_id=item_id).first()  # Fetch item details from the database
        if item:
            cart_items.append({
                'id': item._id,
                'name': item.name,
                'price': item.price,
                'quantity': quantity,
                'total_price': int(item.price) * int(quantity)
            })
            total_cost += int(item.price) * int(quantity)
            total_items += quantity


    # Render the cart page with the processed cart data
    return render_template(
        'cart.html',
        cart_items=cart_items,
        cartCost=total_cost,
        cartItems=total_items
    )

@app.route('/add_to_cart/<int:techId>', methods=['GET', 'POST'])
def addToCartPage(techId):
    print(g.user._id)
    cart = modifyCart(user_id=g.user._id, item_id=techId, action='add', userCookies=session, db=db, userCart=usercarts)
    print(f"{cart}")
    return redirect(url_for('cartPage'))

@app.route('/remove_from_cart/<int:techId>', methods=['GET', 'POST'])
def removeFromCartPage(techId):
    print(g.user._id)
    cart = modifyCart(user_id=g.user._id, item_id=techId, action='remove', userCookies=session, db=db, userCart=usercarts)
    print(cart)
    return redirect(url_for('cartPage'))

@app.route('/products/', methods=['GET', 'POST'])
def productPage():
    form = handleProductForms()
    sellersname = db.session.query(sellers.seller_name, sellers._id).group_by(sellers._id).all()
    form.formSellers.choices = [(seller[1], seller[0]) for seller in sellersname]
    for seller, id in sellersname:
        print(seller, id)
    print('\n', form.formSellers.choices)

    query = technologies.query

    if request.method == 'POST':
        search_query = request.form.get('search', '').strip()
        if search_query:
            query = query.filter(technologies.name.ilike(f"%{search_query}%"))

        selected_sellers = request.form.getlist('formSellers')
        selected_sellers = [int(id) for id in selected_sellers]
        env_impact_threshold = form.env_impact.data
        selected_reviews = form.reviews.data
        min_price = form.minPrice.data
        max_price = form.maxPrice.data

        print(f"Selected Sellers: {selected_sellers}")
        print(f"Selected Reviews: {selected_reviews}")
        print(f"Min Price: {min_price}")
        print(f"Max Price: {max_price}")
        print(f"Environmental Impact Threshold: {env_impact_threshold}") # There are issues with this value, this is to debug.
        query = query.filter(
            technologies.seller_id.in_(selected_sellers),
            technologies.env_impact <= int(env_impact_threshold),
            technologies.reviews >= selected_reviews,
            technologies.price >= min_price,
            technologies.price <= max_price
        ).all()
        print(str(query))
        return render_template('products.html', technologies = query, form = form)
    else:
        # This sets the defaults for the forms so that if the form is not submitted, it shows all products.
        form.formSellers.data = [seller[1] for seller in sellersname]
        form.reviews.data = 0
        form.env_impact.data = 1000
        form.minPrice.data = 0
        form.maxPrice.data = 5000
    return render_template('products.html', technologies = technologies.query.all(), form = form)

@app.route('/checkout/')
def checkoutPage():
    # Check if there are items in the cart
    session_cart = session.get('cart', {})
    if not session_cart:
        # If the cart is empty, redirect to the homepage with an error message
        print("Cart is empty. Redirecting to homepage.")
        return redirect(url_for('galleryPage'))

    # Calculate the total cost of the cart
    total_cost = 0
    total_items = 0
    for item_id_str, quantity in session_cart.items():
        item_id = int(item_id_str)
        item = technologies.query.filter_by(_id=item_id).first()
        if item:
            total_cost += int(item.price) * int(quantity)
            total_items += quantity

    # Load cart from session in to understandable format for the template.
    cart_items = []
    total_cost = 0
    total_items = 0
    for item_id_str, quantity in session_cart.items():
        item_id = int(item_id_str)
        item = technologies.query.filter_by(_id=item_id).first()  # Fetch item details from the database
        if item:
            cart_items.append({
                'id': item._id,
                'name': item.name,
                'price': item.price,
                'quantity': quantity,
                'total_price': int(item.price) * int(quantity)
            })
            total_cost += int(item.price) * int(quantity)
            total_items += quantity

    # Check if the user is logged in
    if int(g.user._id) == 0:
        # If the user is not logged in, show checkout with empty boxes to be filled out
        return render_template(
            'checkout.html',
            logged_in=False,
            cart=session_cart,
            total_cost=total_cost,
            total_items=total_items,
            cart_items=cart_items,
            cartCost=total_cost,
            cartItems=total_items
        )
    else:
        # If the user is logged in, show the checkout page with the order ID and total amount
        order_id = f"ORD-{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}"  # Generate a unique order ID
        return render_template(
            'checkout.html',
            logged_in=True,
            order_id=order_id,
            total_cost=total_cost,
            total_items=total_items,
            user=g.user,
            cart_items=cart_items,
            cartCost=total_cost,
            cartItems=total_items
        )

@app.route('/checkout_check-if-logged-in/')
def checkoutCheckPage():
    # Check if the user is logged in
    print(f"User ID: {g.user._id}")
    if int(g.user._id) == 0:
        return render_template('checkout-confirm.html')
    else:
         return redirect(url_for('checkoutPage'))

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
            return render_template('gateway.html', user = int(g.user._id)) # TODO: If wrong details we need to add a message
    else:
        session['userid'] = 0
        if session.get('userid') == 0:
            print("Cart being erased from session")
            session.pop('cart', None)  # Clear the cart from the session
        session_cookie = encodeFlaskCookie(SECRET_KEY, dict(session))
        return render_template('gateway.html', user = int(g.user._id))


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

@app.route('/clear_cart')
def clear_cart():
    session.pop('cart', None)  # Remove the cart from the session
    print("Cart cleared")
    return redirect(url_for('cartPage'))

# ----------------------------------------------------------
# Creates parameters for the application to run.
# ----------------------------------------------------------
if __name__ == '__main__':
	app.run(
          debug=True,
          host='0.0.0.0',
          port=5000
          )
