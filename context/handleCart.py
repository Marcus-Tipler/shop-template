def handleTest(globalUser, userCart, userCookies):
    print("handleTest function called\n" + str(globalUser) + "\n" + str(userCart) + "\n" + str(userCookies))
    print("Global User to user ID conversion = " + str(globalUser._id))

    # Check if the user is logged in
    if globalUser is None:
        print("User is not logged in")
    else:
        print("User is logged in")
    # For each item in the user cart, check if the item is in the session cookies
    for item in userCart.query.filter_by(userID = globalUser._id):
        print("Item ID: " + str(item.itemIDs))
        if str(item.itemIDs) in userCookies:
            print("Item is in the session cookies")
        else:
            print("Item is not in the session cookies")
    pass