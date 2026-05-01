from flask import Flask, render_template, request, redirect, url_for, session
import sqlite3

app = Flask(__name__)
app.secret_key = "ua_shop_final"

DB_NAME = "ua_shop.db"


# =========================
# DB CONNECTION
# =========================
def connect_db():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn


# =========================
# AUTO FIX DATABASE (SHOES ONLY)
# =========================
def init_db():
    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS products (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        price REAL,
        image TEXT
    )
    """)

    cursor.execute("SELECT COUNT(*) FROM products")
    if cursor.fetchone()[0] == 0:
        cursor.executemany("""
        INSERT INTO products (name, price, image)
        VALUES (?, ?, ?)
        """, [
            ("Nike Air Force 1", 4500, "shoe1.png"),
            ("Adidas Ultraboost", 6500, "shoe2.png"),
            ("Puma RS-X", 4200, "shoe3.png"),
            ("Nike Air Max 1 '87 'Immortal 4'", 7000, "shoe4.png"),
            ("Nike Kobe 5 Protro", 8500, "shoe5.png")
        ])

    conn.commit()
    conn.close()


# =========================
# HOME
# =========================
@app.route("/")
def index():
    conn = connect_db()
    products = conn.execute("SELECT * FROM products").fetchall()
    conn.close()

    cart = session.get("cart", {})
    cart_count = sum(item.get("quantity", 0) for item in cart.values())

    return render_template("index.html",
                           products=products,
                           cart_count=cart_count)


# =========================
# ADD TO CART
# =========================
@app.route("/add_to_cart", methods=["POST"])
def add_to_cart():
    product_id = request.form.get("product_id")
    size = request.form.get("size")

    quantity = int(request.form.get("quantity", 1))

    conn = connect_db()
    product = conn.execute("SELECT * FROM products WHERE id=?", (product_id,)).fetchone()
    conn.close()

    if not product:
        return redirect(url_for("index"))

    cart = session.get("cart", {})
    key = f"{product_id}_{size}"

    if key in cart:
        cart[key]["quantity"] += quantity
    else:
        cart[key] = {
            "id": product["id"],
            "name": product["name"],
            "price": float(product["price"]),
            "image": product["image"],
            "size": size,
            "quantity": quantity
        }

    session["cart"] = cart

    return redirect(url_for("cart"))


# =========================
# BUY NOW
# =========================
@app.route("/buy_now", methods=["POST"])
def buy_now():
    name = request.form.get("name")
    size = request.form.get("size")
    quantity = int(request.form.get("quantity", 1))
    price = float(request.form.get("price", 0))

    total = price * quantity

    return render_template("buy.html",
                           name=name,
                           size=size,
                           quantity=quantity,
                           price=price,
                           total=total)


# =========================
# CART PAGE
# =========================
@app.route("/cart")
def cart():
    cart = session.get("cart", {})
    total = sum(item["price"] * item["quantity"] for item in cart.values())

    return render_template("orders.html",
                           cart=cart,
                           total=total)


# =========================
# REMOVE ITEM
# =========================
@app.route("/remove/<key>")
def remove_item(key):
    cart = session.get("cart", {})

    if key in cart:
        del cart[key]

    session["cart"] = cart
    return redirect(url_for("cart"))


# =========================
# CLEAR CART
# =========================
@app.route("/clear")
def clear_cart():
    session.pop("cart", None)
    return redirect(url_for("cart"))


# =========================
# PAYMENT
# =========================
@app.route("/payment", methods=["POST"])
def payment():
    name = request.form.get("name")
    size = request.form.get("size")

    quantity = int(request.form.get("quantity", 1))
    price = float(request.form.get("price", 0))

    total = price * quantity

    return render_template("payment.html",
                           name=name,
                           size=size,
                           quantity=quantity,
                           price=price,
                           total=total)


# =========================
# PROCESS PAYMENT
# =========================
@app.route("/process_payment", methods=["POST"])
def process_payment():
    number = request.form.get("number")
    pin = request.form.get("pin")

    if number == "09123456789" and pin == "1234":
        session.pop("cart", None)

        return """
        <h2>✅ Payment Successful</h2>
        <p>Your shoe order is confirmed.</p>
        <a href="/">Back to Shop</a>
        """

    return """
    <h2>❌ Payment Failed</h2>
    <a href="/">Try Again</a>
    """


# =========================
# RUN APP
# =========================
if __name__ == "__main__":
    init_db()
    import os

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)