# --------------------------------------------------------------
# Function that processes the user cart and outputs a cost and the cart.
# --------------------------------------------------------------
def handleTest(globalUser, userCart, userCookies):
    # print("handleTest function called\n" + str(globalUser) + "\n" + str(userCart) + "\n" + str(userCookies))
    # print("Global User to user ID conversion = " + str(globalUser._id))

    # # Check if the user is logged in
    # if int(globalUser._id) == 0:
    #     print("User is not logged in")
        
    # else:
    #     print("User is logged in")
    # # For each item in the user cart, check if the item is in the session cookies
    # for item in userCart.query.filter_by(userID = globalUser._id):
    #     print("Item ID: " + str(item.itemIDs))
    #     if str(item.itemIDs) in userCookies:
    #         print("Item is in the session cookies")
    #     else:
    #         print("Item is not in the session cookies")

    userCart = updateCartCookie(globalUser, userCart, userCookies)
    print("Updated user cart: " + str(userCart))
    return userCart, 0


# --------------------------------------------------------------
# Output an updated cookie cart with the items in the user cart
# --------------------------------------------------------------
def updateCartCookie(globalUser, userCart, userCookies):
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
        # Apply newly made cart session to the Database to ensure it remains up to date on other devices.
        print("User cart: " + str(userCart))
        userCookies['cart'] = cart
        return userCookies, 0