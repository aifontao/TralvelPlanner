from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash

from helpers import apology, login_required

#Configure application
app = Flask(__name__)
# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 library to use SQLite database
db = SQL("sqlite:///travel.db")


@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


@app.route("/")
@login_required
def index():
    """Show user dashboard"""

    trips = db.execute("SELECT name, country, city FROM trips WHERE user_id = ?", session["user_id"])

    return render_template("index.html", trips=trips)


@app.route("/account", methods=["GET", "POST"])
@login_required
def account():
    """Show users account"""

    account = db.execute(
        "SELECT username FROM users WHERE id = ?", session["user_id"])

    return render_template("account.html", account=account)


import os
print("DB path:", os.path.abspath("travel.db"))


@app.route("/add", methods=["GET", "POST"])
@login_required
def add():

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        country = request.form.get("country")
        city = request.form.get("city")
        
        print("Form submitted with:", country, city)

        if not country or not city:
            return apology("Missing country", 400)
        
        
        try:
            db.execute("INSERT INTO trips (user_id, country, city) VALUES (?, ?, ?)",
                    session["user_id"], country, city)
        except Exception as e:
            print("DB Error:", e)
            return apology("Database error", 500)

        return redirect("/")

    return render_template("add.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 403)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 403)

        # Query database for username
        rows = db.execute(
            "SELECT * FROM users WHERE username = ?", request.form.get("username")
        )

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(
            rows[0]["hash"], request.form.get("password")
        ):
            return apology("invalid username and/or password", 403)

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")


@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")


@app.route("/password", methods=["GET", "POST"])
@login_required
def password():
    """Change users password"""

    if request.method == "POST":

        # Get current password hash
        pwhash = db.execute("SELECT hash FROM users WHERE id = ?", session["user_id"])
        pwhash = pwhash[0]["hash"]

        # Check for possible errors
        # If the user does not input any current passord
        current = request.form.get("current")
        if not current or not check_password_hash(pwhash, current):
            return apology("Current password is incorrect", 400)

        # If the user doesn't type any new password
        password = request.form.get("password")
        if not password:
            return apology("Missing new password", 400)
        # or if the new password is the same as the old password
        if check_password_hash(pwhash, password):
            return apology("The new password must be different from the current password", 400)

        # If the user doesn't type any confirmation or if it does not match the new password
        confirmation = request.form.get("confirmation")
        if not confirmation or password != confirmation:
            return apology("New passwords don't match", 400)

        # Hash new password
        hash = generate_password_hash(password, method='scrypt', salt_length=16)
        # update user password in the users dictionary
        db.execute("UPDATE users SET hash = ? WHERE hash = ? AND id = ?",
                   hash, pwhash, session["user_id"])

        flash("Your password has been successfully changed!", "success")
        return redirect("/account")

    return render_template("password.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""

    if request.method == "POST":

        # Check for possible errors
        name = request.form.get("username")
        if not name:
            return apology("Missing usermane", 400)

        password = request.form.get("password")
        if not password:
            return apology("Missing password", 400)

        confirmation = request.form.get("confirmation")
        if not confirmation or password != confirmation:
            return apology("Passwords don't match", 400)

        hash = generate_password_hash(password, method='scrypt', salt_length=16)
        # Insert the new user into users table
        try:
            # If username is already taken
            db.execute("INSERT INTO users (username, hash) VALUES(?, ?)", name, hash)
            return redirect("/")
        except ValueError:
            return apology("Username is already taken - choose another unsername", 400)

    # Log user in
    return render_template("register.html")


if __name__ == "__main__":
    app.run(debug=True)