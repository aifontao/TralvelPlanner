from datetime import datetime

from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash

from helpers import apology, login_required

# Import image API to display photos of the cities - Learned on Shecodes Workshop

import requests

PEXELS_API_KEY = "d7bDbjgQNBsos5CD1RYTFipJzV9I0Kst00wjilfajFe0I6JEhBznKJbu"

def get_city_image(city):
    try:
        headers = {"Authorization": PEXELS_API_KEY}
        params = {"query": city, "per_page":1}
        response = requests.get("https://api.pexels.com/v1/search", headers=headers, params=params)
        data = response.json()
        if data["photos"]:
            return data["photos"][0]["src"]["large"]
    except Exception as e:
        print("Error searching for photo:", e)
    return None

# Configure application
app = Flask(__name__)
# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

STATUS = ["Visited", "Ongoing", "Scheduled", "Planning", "Wishlist"]
TYPES = ["Holiday", "Adventure", "Romantic", "Solo", "Work"]
RELATIONSHIP = ["Family", "Partner", "Friend", "Coworker"]
EXPERIENCES = ["Activity", "Place", "Food"]

# Configure CS50 library to use SQLite database
db = SQL("sqlite:///travel.db")


# Searched chatGPT on how to use Context Processor so that the trips are available globally
@app.context_processor
def inject_trips():
    # If user is not logged in, return and empty dict
    if "user_id" not in session:
        return {}
    # Otherwise, return all trips for the logged-in user
    user_trips = db.execute("SELECT id, name, country, city FROM trips WHERE user_id = ?", session["user_id"])
    
    # Define status, types, relationship and experiences options (for dropdown)
    status = STATUS
    types = TYPES
    relationship = RELATIONSHIP
    experiences = EXPERIENCES

    # Return the data to be available globally in templates
    return {"trips": user_trips, "status": status, "types": types, "relationship": relationship, "experiences": experiences}


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

    trips = db.execute("SELECT id, name, country, city FROM trips WHERE user_id = ?", session["user_id"])
    print(trips[0])
    # Show image of each trip - Used ChatGPT to add this feature
    enriched_trips = []
    for trip in trips:
        trip_copy = trip.copy()
        image_url = get_city_image(trip["city"])
        trip_copy["image_url"] = image_url
        enriched_trips.append(trip_copy)
    print(enriched_trips[0])
    return render_template("index.html", trips=enriched_trips)


@app.route("/account", methods=["GET", "POST"])
@login_required
def account():
    """Show users account"""

    account = db.execute(
        "SELECT username FROM users WHERE id = ?", session["user_id"])

    return render_template("account.html", account=account)


@app.route("/add_trip", methods=["GET", "POST"])
@login_required
def add_trip():

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        name = (request.form.get("name") or "").strip() or None
        country = (request.form.get("country") or "").strip()
        city = (request.form.get("city") or "").strip()
        status = request.form.get("status") or None
        trip_type = request.form.get("type") or None
            
        if not country or not city:
            return apology("Missing country or city", 400)

        now = datetime.now().strftime('%Y-%m-%d')

        try:
            db.execute(
                "INSERT INTO trips (user_id, name, country, city, status, trip_type, date_created) VALUES (?, ?, ?, ?, ?, ?, ?)",
                session["user_id"], name, country, city, status, trip_type, now
            )
        except Exception as e:
            print("Database insert error:", e)
            return apology("Failed to add trip")

        flash("Trip added successfully! ☺️")
        return redirect("/")

    return render_template("add_trip.html")


@app.route("/trip/<int:trip_id>/add_buddy", methods=["GET", "POST"])
@login_required
def add_buddy(trip_id):
    if request.method == "POST":
        buddy_name = request.form.get("buddy_name", "").strip() 
        relationship = request.form.get("relationship")
                
        if not buddy_name or not relationship:
            return apology("Missing buddy name or relationship", 400)

        try:
            db.execute(
                "INSERT INTO buddies (trip_id, name, relationship_type) VALUES (?, ?, ?)",
                trip_id, buddy_name, relationship
                )
            flash("Buddy added successfully!")
        except Exception as e:
            print("[ERROR] Failed to add buddy:", e)
            return apology("Failed to add buddy", 500)
             
        return redirect(f"/trip/{trip_id}")

    trip_data = db.execute(
        "SELECT * FROM trips WHERE id = ? AND user_id = ?", trip_id, session["user_id"]
    )
    if not trip_data:
        return apology("Trip not found", 404)
        
    return render_template("add_buddy.html", trip=trip_data[0])

@app.route("/delete_trip/<int:trip_id>", methods=["POST"])
@login_required
def delete_trip(trip_id):
    
    # If the user confirms they want to delete trip
    # Check if trip exists for this user
    trip = db.execute("SELECT * FROM trips WHERE id = ? AND user_id = ?", trip_id, session["user_id"])
    if not trip:
        return apology("Trip not found or unauthorized")

    db.execute("DELETE FROM trips WHERE id = ? AND user_id = ?", trip_id, session["user_id"])            
        
    flash("Trip deleted successfully!")
    return redirect("/")
        

# Searched chatGPT to understand how to change the route parameter to a given trip_id
@app.route("/edit_trip/<int:trip_id>", methods=["GET", "POST"])
@login_required
def edit_trip(trip_id):

    # On GET - show trip details
    trip_data = db.execute("SELECT * FROM trips WHERE id = ? AND user_id = ?", trip_id, session["user_id"])
    if not trip_data:
        return apology("Trip not found", 404)
    
    trip = trip_data[0]

    # Handle form submission for editing
    if request.method == "POST":
        # Use submitted value or keep current one
        trip_name = request.form.get("trip_name_new") or trip["name"]
        country = request.form.get("country_new") or trip["country"]
        city = request.form.get("city_new") or trip["city"]
        status = request.form.get("status_new") or trip["status"]
        trip_type = request.form.get("trip_type_new") or trip["trip_type"]
        notes = request.form.get("notes_new") or trip["notes"]

        # Only handle rating if status is "Visited"
        if status == "Visited":
            rating = request.form.get("rating_new")
            try:
                # Convert rating to int if provided
                rating = int(rating) if rating else trip["rating"]
                # Validate rating range
                if rating < 1 or rating > 5:
                    flash("Rating must be between 1 and 5")
                    return redirect(f"/edit_trip/{trip_id}")
            except ValueError:
                flash("Rating must be a number")
                return redirect(f"/edit_trip/{trip_id}")
        else:
            rating = None

        db.execute(
                "UPDATE trips SET name = ?, country = ?, city = ?, notes = ?, trip_type = ?, status = ?, rating = ? WHERE id = ? AND user_id = ?",
                trip_name, country, city, notes, trip_type, status, rating, trip_id, session["user_id"]
                )

        flash("Trip updated successfully! ☺️")
        return redirect(f"/trip/{trip_id}")
    
    return render_template("edit_trip.html", trip=trip)


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
            return apology("Please enter new password", 400)
        # or if the new password is the same as the old password
        if check_password_hash(pwhash, password):
            return apology("The new password must be different from the current password", 400)

        # If the user doesn't type any confirmation or if it does not match the new password
        confirmation = request.form.get("confirmation")
        if not confirmation or password != confirmation:
            return apology("Password confirmation does not match", 400)

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


# Searched chatGPT to understand how to change the route parameter to a given trip_id
@app.route("/trip/<int:trip_id>", methods=["GET"])
@login_required
def view_trip(trip_id):

    # On GET - show trip details
    trip = db.execute("SELECT * FROM trips WHERE id = ? AND user_id = ?", trip_id, session["user_id"])
    if not trip:
        return apology("Trip not found", 404)
    
    buddies = db.execute("SELECT * FROM buddies WHERE trip_id = ?", trip_id)
    image_url = get_city_image(trip[0]["city"])

    return render_template("trip.html", trip=trip[0], buddies=buddies, image_url=image_url)

if __name__ == "__main__":
    app.run(debug=True)
