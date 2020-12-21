import json
import requests
import os

from cs50 import SQL
from flask import Flask, flash, jsonify, redirect, render_template, request, session
from flask_session import Session
from math import radians, cos, sin, asin, sqrt
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from werkzeug.security import check_password_hash, generate_password_hash

from helpers import apology, login_required

# Configure application
app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Ensure responses aren't cached
@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///users.db")


@app.route("/")
@login_required
def index():
    id = session["user_id"]

    ip = request.remote_addr

    current_lat = 36.2807
    current_long = -80.3592

    locations = db.execute("SELECT * FROM locations WHERE id = :id", id=id)

    for location in locations:
        lat = location["lat"]
        long = location["long"]
        distance = round(haversine(current_long, current_lat, long, lat))
        distance = {"distance": distance}
        location.update(distance)

    return render_template(
        "index.html",
        locations=locations,
        current_lat=current_lat,
        current_long=current_long,
        ip=ip,
    )


def haversine(lon1, lat1, lon2, lat2):
    """
    Calculate the great circle distance between two points
    on the earth (specified in decimal degrees)
    """
    # convert decimal degrees to radians
    lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])

    # haversine formula
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
    c = 2 * asin(sqrt(a))
    r = 3965
    return c * r


@app.route("/add", methods=["GET", "POST"])
@login_required
def add():
    """Add a location"""

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        id = session["user_id"]
        location = request.form.get("location")

        search_string = "https://nominatim.openstreetmap.org/search?q={}&format=json&limit=1".format(
            location
        )
        location_info = requests.get(search_string)
        location_info = json.loads(location_info.text)[0]

        lat = float(location_info["lat"])
        long = float(location_info["lon"])

        db.execute("INSERT INTO locations VALUES (?, ?, ?, ?)", id, location, lat, long)

        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("add.html")


@app.route("/delete", methods=["GET", "POST"])
@login_required
def delete():
    """Delete a location"""

    id = session["user_id"]

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        location = request.form.get("location")

        db.execute(
            "DELETE FROM locations WHERE id = :id AND location = :location",
            id=id,
            location=location,
        )

        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        locations = db.execute("SELECT location FROM locations WHERE id = :id", id=id)

        return render_template("delete.html", locations=locations)


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
            "SELECT * FROM users WHERE username = :username",
            username=request.form.get("username"),
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


@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 403)

        # Ensure username is not already in use
        users = db.execute("SELECT username FROM users")
        for user in users:
            if request.form.get("username") == user["username"]:
                return apology("username already taken", 403)

        # Ensure password was submitted
        if not request.form.get("password"):
            return apology("must provide password", 403)

        # Ensure password confirmation was submitted
        elif not request.form.get("confirmation"):
            return apology("must provide confirmation of password", 403)

        # Ensure password and confirmation match
        elif not request.form.get("password") == request.form.get("confirmation"):
            return apology("passwords do not match", 403)

        # Hash password
        hashed = generate_password_hash(
            request.form.get("password"), method="pbkdf2:sha256", salt_length=8
        )

        # Insert Username and Password into database
        db.execute(
            "INSERT INTO users (username, hash) VALUES (?, ?)",
            request.form.get("username"),
            hashed,
        )

        return redirect("/")

    else:
        return render_template("register.html")


def errorhandler(e):
    """Handle error"""
    if not isinstance(e, HTTPException):
        e = InternalServerError()
    return apology(e.name, e.code)


# Listen for errors
for code in default_exceptions:
    app.errorhandler(code)(errorhandler)
