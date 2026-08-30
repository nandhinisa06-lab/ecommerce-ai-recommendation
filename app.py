from flask import Flask, render_template, request, redirect, url_for
import mysql.connector
from dotenv import load_dotenv
import os

load_dotenv()

app = Flask(__name__)
def get_db_connection():
    return mysql.connector.connect(
        host=os.getenv("MYSQL_HOST"),
        user=os.getenv("MYSQL_USER"),
        password=os.getenv("MYSQL_PASSWORD"),
        database=os.getenv("MYSQL_DATABASE")
    )



@app.route("/")
def home():
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    cursor.execute("SELECT * FROM products")
    products = cursor.fetchall()

    cursor.close()
    connection.close()

    return render_template("index.html", products=products)


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        name = request.form["name"]
        email = request.form["email"]
        password = request.form["password"]

        connection = get_db_connection()
        cursor = connection.cursor()

        cursor.execute(
            "INSERT INTO users (name, email, password) VALUES (%s, %s, %s)",
            (name, email, password)
        )

        connection.commit()

        cursor.close()
        connection.close()

        return redirect(url_for("login"))

    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)

        cursor.execute(
            "SELECT * FROM users WHERE email = %s AND password = %s",
            (email, password)
        )

        user = cursor.fetchone()

        cursor.close()
        connection.close()

        if user:
            return f"Welcome, {user['name']}! 🎉"

        return "Invalid email or password ❌"

    return render_template("login.html")
@app.route("/recommendations")
def recommendations():
    category = request.args.get("category")

    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    if category:
        cursor.execute(
            "SELECT * FROM products WHERE category = %s",
            (category,)
        )
    else:
        cursor.execute("SELECT * FROM products")

    products = cursor.fetchall()

    cursor.close()
    connection.close()

    return render_template(
        "recommendations.html",
        products=products,
        category=category
    )
@app.route("/set-preference", methods=["POST"])
def set_preference():
    category = request.form["category"]

    connection = get_db_connection()
    cursor = connection.cursor()

    cursor.execute(
        "UPDATE users SET preferred_category = %s WHERE email = %s",
        (category, "test@example.com")
    )

    connection.commit()

    cursor.close()
    connection.close()

    return redirect(
        url_for("recommendations", category=category)
    )
@app.route("/preference")
def preference():
    return render_template("preference.html")

if __name__ == "__main__":
    app.run(debug=True)
