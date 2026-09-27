from flask import Flask, render_template, request, redirect, url_for, session
from recommendation import recommend_products
import pandas as pd
import random
from datetime import datetime

app = Flask(__name__)

app.secret_key = "shopsmart-secret-key"


# =========================
# Login Required Function
# =========================

def login_required():

    if "username" not in session:
        return False

    return True


# =========================
# Home
# =========================

@app.route("/")
def home():

    if "username" not in session:
        return redirect(url_for("login"))

    return render_template("index.html")


# =========================
# Signup
# =========================

@app.route("/signup", methods=["GET", "POST"])
def signup():

    if request.method == "POST":

        username = request.form["username"].strip()
        password = request.form["password"]

        if not username or not password:
            return render_template(
                "signup.html"
            )

        session["username"] = username

        return redirect(url_for("home"))

    return render_template("signup.html")


# =========================
# Login
# =========================

@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        username = request.form["username"].strip()
        password = request.form["password"]

        if not username or not password:
            return render_template(
                "login.html"
            )

        session["username"] = username

        return redirect(url_for("home"))

    return render_template("login.html")


# =========================
# Logout
# =========================

@app.route("/logout")
def logout():

    session.clear()

    return redirect(url_for("login"))


# =========================
# Profile
# =========================

@app.route("/profile")
def profile():

    if not login_required():
        return redirect(url_for("login"))

    username = session.get("username")

    return render_template(
        "profile.html",
        username=username
    )


# =========================
# Edit Profile
# =========================

@app.route("/edit_profile", methods=["GET", "POST"])
def edit_profile():

    if not login_required():
        return redirect(url_for("login"))

    username = session.get("username")

    if request.method == "POST":

        new_username = request.form["username"].strip()
        phone = request.form["phone"].strip()
        address = request.form["address"].strip()

        if new_username:
            session["username"] = new_username

        session["phone"] = phone
        session["address"] = address

        return redirect(url_for("profile"))

    phone = session.get(
        "phone",
        ""
    )

    address = session.get(
        "address",
        ""
    )

    return render_template(
        "edit_profile.html",
        username=username,
        phone=phone,
        address=address
    )


# =========================
# Products
# =========================

@app.route("/products")
def products():

    if not login_required():
        return redirect(url_for("login"))

    products = pd.read_csv(
        "products.csv"
    )

    return render_template(
        "products.html",
        products=products.to_dict("records")
    )


# =========================
# Product Details
# =========================

@app.route("/product")
def product():

    if not login_required():
        return redirect(url_for("login"))

    product_id = request.args.get(
        "id",
        default=1,
        type=int
    )

    products = pd.read_csv(
        "products.csv"
    )

    selected_product = products[
        products["id"] == product_id
    ]

    if selected_product.empty:
        return redirect(url_for("products"))

    selected_product = selected_product.iloc[0]

    recommendations = recommend_products(
        product_id
    )

    # Get ratings

    ratings = session.get(
        "ratings",
        {}
    )

    product_ratings = ratings.get(
        str(product_id),
        []
    )

    # Calculate average rating

    if product_ratings:

        average_rating = round(
            sum(product_ratings) /
            len(product_ratings),
            1
        )

        rating_count = len(
            product_ratings
        )

    else:

        average_rating = 0
        rating_count = 0

    return render_template(
        "product.html",
        product=selected_product,
        recommendations=recommendations,
        average_rating=average_rating,
        rating_count=rating_count
    )


# =========================
# Rate Product
# =========================

@app.route(
    "/rate_product",
    methods=["POST"]
)
def rate_product():

    if not login_required():
        return redirect(url_for("login"))

    product_id = request.form[
        "product_id"
    ]

    rating = request.form[
        "rating"
    ]

    ratings = session.get(
        "ratings",
        {}
    )

    if product_id not in ratings:
        ratings[product_id] = []

    ratings[product_id].append(
        int(rating)
    )

    session["ratings"] = ratings
    session.modified = True

    return redirect(
        url_for(
            "product",
            id=int(product_id)
        )
    )


# =========================
# Home Search
# =========================

@app.route("/search")
def search():

    if not login_required():
        return redirect(url_for("login"))

    search_text = request.args.get(
        "query",
        ""
    ).strip().lower()

    products = pd.read_csv(
        "products.csv"
    )

    matching_products = products[
        products["name"]
        .str.lower()
        .str.contains(
            search_text,
            na=False
        )
    ]

    if not matching_products.empty:

        product_id = int(
            matching_products.iloc[0]["id"]
        )

        return redirect(
            url_for(
                "product",
                id=product_id
            )
        )

    return redirect(
        url_for("products")
    )


# =========================
# Add to Cart
# =========================

@app.route("/add_to_cart")
def add_to_cart():

    if not login_required():
        return redirect(url_for("login"))

    product_id = request.args.get(
        "id",
        type=int
    )

    if (
        "cart" not in session
        or not isinstance(
            session["cart"],
            dict
        )
    ):

        session["cart"] = {}

    cart = session["cart"]

    product_id = str(product_id)

    cart[product_id] = (
        cart.get(product_id, 0) + 1
    )

    session["cart"] = cart
    session.modified = True

    return redirect(
        url_for(
            "product",
            id=int(product_id)
        )
    )


# =========================
# Add to Wishlist
# =========================

@app.route("/add_to_wishlist")
def add_to_wishlist():

    if not login_required():
        return redirect(url_for("login"))

    product_id = request.args.get(
        "id",
        type=int
    )

    wishlist = session.get(
        "wishlist",
        []
    )

    if product_id not in wishlist:

        wishlist.append(
            product_id
        )

    session["wishlist"] = wishlist
    session.modified = True

    return redirect(
        url_for(
            "product",
            id=product_id
        )
    )


# =========================
# Remove from Wishlist
# =========================

@app.route("/remove_from_wishlist")
def remove_from_wishlist():

    if not login_required():
        return redirect(url_for("login"))

    product_id = request.args.get(
        "id",
        type=int
    )

    wishlist = session.get(
        "wishlist",
        []
    )

    if product_id in wishlist:

        wishlist.remove(
            product_id
        )

    session["wishlist"] = wishlist
    session.modified = True

    return redirect(
        url_for("wishlist")
    )


# =========================
# Wishlist
# =========================

@app.route("/wishlist")
def wishlist():

    if not login_required():
        return redirect(url_for("login"))

    wishlist = session.get(
        "wishlist",
        []
    )

    products = pd.read_csv(
        "products.csv"
    )

    wishlist_products = products[
        products["id"].isin(
            wishlist
        )
    ].to_dict("records")

    return render_template(
        "wishlist.html",
        wishlist_products=wishlist_products
    )


# =========================
# Cart
# =========================

@app.route("/cart")
def cart():

    if not login_required():
        return redirect(url_for("login"))

    cart = session.get(
        "cart",
        {}
    )

    products = pd.read_csv(
        "products.csv"
    )

    cart_products = []

    for product_id, quantity in cart.items():

        product = products[
            products["id"] == int(product_id)
        ]

        if not product.empty:

            product = (
                product.iloc[0]
                .to_dict()
            )

            product["quantity"] = int(
                quantity
            )

            product["subtotal"] = (
                int(product["price"])
                * int(quantity)
            )

            cart_products.append(
                product
            )

    total = sum(
        int(product["subtotal"])
        for product in cart_products
    )

    return render_template(
        "cart.html",
        cart_products=cart_products,
        total=total
    )


# =========================
# Checkout
# =========================

@app.route("/checkout")
def checkout():

    if not login_required():
        return redirect(url_for("login"))

    cart = session.get(
        "cart",
        {}
    )

    if not cart:
        return redirect(
            url_for("cart")
        )

    products = pd.read_csv(
        "products.csv"
    )

    cart_products = []

    for product_id, quantity in cart.items():

        product = products[
            products["id"] == int(product_id)
        ]

        if not product.empty:

            product = (
                product.iloc[0]
                .to_dict()
            )

            product["quantity"] = int(
                quantity
            )

            product["subtotal"] = (
                int(product["price"])
                * int(quantity)
            )

            cart_products.append(
                product
            )

    total = sum(
        int(product["subtotal"])
        for product in cart_products
    )

    return render_template(
        "checkout.html",
        cart_products=cart_products,
        total=total
    )


# =========================
# Place Order
# =========================

@app.route("/place_order")
def place_order():

    if not login_required():
        return redirect(url_for("login"))

    cart = session.get(
        "cart",
        {}
    )

    if not cart:
        return redirect(
            url_for("cart")
        )

    customer_name = request.args.get(
        "name",
        ""
    ).strip()

    customer_phone = request.args.get(
        "phone",
        ""
    ).strip()

    customer_address = request.args.get(
        "address",
        ""
    ).strip()

    products = pd.read_csv(
        "products.csv"
    )

    total = 0

    for product_id, quantity in cart.items():

        product = products[
            products["id"] == int(product_id)
        ]

        if not product.empty:

            price = product.iloc[0][
                "price"
            ]

            total += (
                int(price)
                * int(quantity)
            )

    order_id = (
        "ORD"
        + str(
            random.randint(
                10000,
                99999
            )
        )
    )

    orders = session.get(
        "orders",
        []
    )

    current_date = (
        datetime.now()
        .strftime(
            "%d-%m-%Y %H:%M"
        )
    )

    orders.append({

        "order_id": order_id,

        "date": current_date,

        "name": customer_name,

        "phone": customer_phone,

        "address": customer_address,

        "total": int(total),

        "status": "Order Placed"
    })

    session["orders"] = orders

    session["cart"] = {}

    session.modified = True

    return render_template(
        "order_success.html",
        total=int(total),
        order_id=order_id
    )


# =========================
# Order History
# =========================

@app.route("/orders")
def orders():

    if not login_required():
        return redirect(url_for("login"))

    orders = session.get(
        "orders",
        []
    )

    return render_template(
        "orders.html",
        orders=orders
    )


# =========================
# Increase Quantity
# =========================

@app.route("/increase_quantity")
def increase_quantity():

    if not login_required():
        return redirect(url_for("login"))

    product_id = request.args.get(
        "id",
        type=int
    )

    cart = session.get(
        "cart",
        {}
    )

    product_id = str(product_id)

    if product_id in cart:

        cart[product_id] += 1

    session["cart"] = cart
    session.modified = True

    return redirect(
        url_for("cart")
    )


# =========================
# Decrease Quantity
# =========================

@app.route("/decrease_quantity")
def decrease_quantity():

    if not login_required():
        return redirect(url_for("login"))

    product_id = request.args.get(
        "id",
        type=int
    )

    cart = session.get(
        "cart",
        {}
    )

    product_id = str(product_id)

    if product_id in cart:

        cart[product_id] -= 1

        if cart[product_id] <= 0:

            del cart[product_id]

    session["cart"] = cart
    session.modified = True

    return redirect(
        url_for("cart")
    )


# =========================
# Remove from Cart
# =========================

@app.route("/remove_from_cart")
def remove_from_cart():

    if not login_required():
        return redirect(url_for("login"))

    product_id = request.args.get(
        "id",
        type=int
    )

    cart = session.get(
        "cart",
        {}
    )

    product_id = str(product_id)

    if product_id in cart:

        del cart[product_id]

    session["cart"] = cart
    session.modified = True

    return redirect(
        url_for("cart")
    )


# =========================
# Run Application
# =========================

if __name__ == "__main__":

    app.run(
        debug=True
    )