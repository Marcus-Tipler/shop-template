# --------------------------------------------------------------
# Function that processes the user cart and outputs a cost and the cart.
# --------------------------------------------------------------
def handleTest(globalUser, userCart, userCookies, db, technologies):
    userCart = updateCartCookie(globalUser, userCart, userCookies, db, technologies)
    print("Updated user cart: " + str(userCart))
    return userCart, 0


# --------------------------------------------------------------
# Output an updated cookie cart with the items in the user cart
# --------------------------------------------------------------
def updateCartCookie(globalUser, userCart, userCookies, db, technologies):
    # Check if the user is logged in
    cart = userCookies.get('cart', {})
    user_id = int(globalUser._id)

    if user_id == 0:
        print("User is not logged in")
        return userCookies, 0
    else:
        print("User is logged in")
    # For each item in the user cart, check if the item is in the session cookies
        for item in userCart.query.filter_by(userID = user_id):
            item_id_str = item.itemIDs
            print("Item ID: " + item_id_str)
            print("User Cookies: " + str(userCookies))
            print("Boolean Result: " + str(item_id_str in cart))

            if item_id_str in cart:
                print("Item is in the session cookies")
            else:
                print("Item is not in the session cookies")

                if item_id_str not in cart:
                    cart[item_id_str] = 0
                
                cart[item_id_str] += int(item.amount)
            # Add the item to the session cookies
        print("User cart: " + str(userCart))
        userCookies['cart'] = cart

        # Apply newly made cart session to the Database to ensure it remains up to date on other devices.
        print("Updating Cart Database")
        updateCartDatabase(userCookies, userCart, user_id, db)
        print("Cart updated successfully")
        totalPrice = updateCostTotal(cart, technologies)
        return userCookies, totalPrice
    

# --------------------------------------------------------------
# Update the database with the cart session information
# --------------------------------------------------------------
def updateCartDatabase(userCookies, userCart, user_id, db):
    # Clear the existing cart for the user
    userCart.query.filter_by(userID=user_id).delete()

    # Add the items from the session cookies to the database
    for item_id_str, amount in userCookies['cart'].items():
        item_id = int(item_id_str)
        new_cart_item = userCart(userID=user_id, itemIDs=item_id, amount=amount)
        db.session.add(new_cart_item)  # Use SQLAlchemy's session to add the new item

        print(f"Adding item to database: userID={user_id}, itemID={item_id}, amount={amount}")
    # Commit the changes to the database
    db.session.commit()
    print("Database updated successfully to: ")
    for item in userCart.query.filter_by(userID=user_id):
        print("Item ID: " + str(item.itemIDs) + " Amount: " + str(item.amount))
    return


# --------------------------------------------------------------
#  Calculate the total cost of the cart
# --------------------------------------------------------------
def updateCostTotal(cart, technologies):
    totalPrice = 0
    for item_id_str, amount in cart.items():
        item_id = int(item_id_str)
        item = technologies.query.filter_by(_id=item_id).first()
        if item:
            print("Item ID: " + str(item._id) + " Amount: " + str(amount))
            totalPrice += int(item.price) * int(amount)
    print("Total Price: " + str(totalPrice))
    return totalPrice


# --------------------------------------------------------------
#  Modify the cart by adding or removing items
# --------------------------------------------------------------
def modifyCart(user_id, item_id, action, userCookies, db, userCart):
    # Ensure the cart exists in the session
    cart = userCookies.get('cart', {})

    # Convert item_id to string for consistency in the cart dictionary
    item_id_str = str(item_id)

    if action == 'add':
        # Add the item to the cart
        if item_id_str not in cart:
            cart[item_id_str] = 0
        cart[item_id_str] += 1  # Increment the quantity
        print(f"Added item {item_id} to the cart. New quantity: {cart[item_id_str]}")

    elif action == 'remove':
        # Remove the item from the cart
        if item_id_str in cart:
            cart[item_id_str] -= 1  # Decrement the quantity
            if cart[item_id_str] <= 0:
                del cart[item_id_str]  # Remove the item if quantity is 0
            print(f"Removed item {item_id} from the cart.")
        else:
            print(f"Item {item_id} not found in the cart.")

    else:
        print("Invalid action. Use 'add' or 'remove'.")

    # Update the session cart
    userCookies['cart'] = cart

    # Update the database to reflect the changes
    print(f"THE USER ID IS {user_id.strip()}")
    if int(user_id) != 0: 
        print("Updating Cart Database LINE 124")
        updateCartDatabase(userCookies, userCart, user_id, db)

    return cart