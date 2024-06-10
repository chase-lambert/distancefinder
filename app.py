import json
import os
import requests

from flask import Flask, flash, jsonify, redirect, render_template, request, session
from flask_session import Session
from math import radians, cos, sin, asin, sqrt
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from werkzeug.security import check_password_hash, generate_password_hash

from helpers import apology

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


@app.route("/", methods=["GET", "POST"])
def index():

    destinations = [{'location': 'King, NC', 'lat': 36.280694, 'long': -80.3592197}, {'location': 'Dudley, NC', 'lat': 35.2673857, 'long': -78.0374891}, {'location': 'Edinburgh, Scotland', 'lat': 55.9533456, 'long': -3.1883749}, {'location': 'Medellin, Colombia', 'lat': 6.2443382, 'long': -75.573553}, {'location': 'Redgranite, WI', 'lat': 44.0419238, 'long': -89.0984504}, {'location': 'Marana, AZ', 'lat': 32.4446988, 'long': -111.2157091}, {'location': 'Fairfield, CA', 'lat': 38.2493581, 'long': -122.039966}, {'location': 'Yigo, Guam', 'lat': 13.535204499999999, 'long': 144.89715694673106}]

    locations = [{'location': ""}, {'location': 'King, NC', 'lat': 36.345930, 'long': -80.295900}, {'location': 'Fort Payne, Alabama', 'lat': 34.4442547, 'long': -85.7196893}, {'location': 'Hot Springs, Arkansas', 'lat': 34.5038393, 'long': -93.0552437}, {'location': 'Canyon, Texas', 'lat': 34.99253385, 'long': -101.92788331921604}, {'location': 'Pena Blanca, New Mexico', 'lat': 35.574754999999996, 'long': -106.33723818363845}, {'location': 'Williams, AZ', 'lat': 35.2503394, 'long': -112.1869481}, {'location': 'Springfield, Utah', 'lat': 37.1908427, 'long': -93.2932611}, {'location': 'Torrey, Utah', 'lat': 38.2997368, 'long': -111.4204705}, {'location': 'Moab, Utah', 'lat': 38.5738096, 'long': -109.5462146}, {'location': 'Ashton, Idaho', 'lat': 44.071581, 'long': -111.448288}, {'location': 'Browning, Montana', 'lat': 48.557743, 'long': -113.0172586}, {'location': 'Custer, South Dakota', 'lat': 43.6726477, 'long': -103.5101597}, {'location': 'Redgranite, WI', 'lat': 44.0419238, 'long': -89.0984504}, {'location': 'Marana, AZ', 'lat': 32.4446988, 'long': -111.2157091}]

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        current = locations[1]

        if request.form.get("location"):
            current = request.form.get("location")

            for location in locations:
                if location["location"] == current:
                    current_destination = location

            current_lat = current_destination["lat"]
            current_long = current_destination["long"]

            for destination in destinations:
                lat = destination["lat"]
                long = destination["long"]
                distance = round(haversine(current_long, current_lat, long, lat))
                distance = {"distance": distance}
                destination.update(distance)

            return render_template(
                "index.html",
                current=current,
                destinations=destinations,
                locations=locations,
            )

        if request.form.get("new_location"):
            current = request.form.get("new_location")
            search_string = "https://nominatim.openstreetmap.org/search?q={}&format=json&limit=1".format(current)
            location_info = requests.get(search_string)
            location_info = json.loads(location_info.text)[0]

            current_lat = float(location_info["lat"])
            current_long = float(location_info["lon"])
            
            for destination in destinations:
                lat = destination["lat"]
                long = destination["long"]
                distance = round(haversine(current_long, current_lat, long, lat))
                distance = {"distance": distance}
                destination.update(distance)

            return render_template(
                "index.html",
                current=current,
                destinations=destinations,
                locations=locations,
            )

        # if request.form.get("destination"):
        #     new_destination = request.form.get("destination")
        #     search_string = "https://nominatim.openstreetmap.org/search?q={}&format=json&limit=1".format(new_destination)
        #     location_info = requests.get(search_string)
        #     location_info = json.loads(location_info.text)[0]
        #     lat = float(location_info["lat"])
        #     long = float(location_info["lon"])
        #     new_destination = {"location": new_destination, "lat": lat, "long": long}
        #     destinations.append(new_destination)

        #     current_lat = current["lat"]
        #     current_long = current["long"]

        #     for destination in destinations:
        #         lat = destination["lat"]
        #         long = destination["long"]
        #         distance = round(haversine(current_long, current_lat, long, lat))
        #         distance = {"distance": distance}
        #         destination.update(distance)

        #     return render_template(
        #         "index.html",
        #         current=current["location"],
        #         destinations=destinations,
        #         locations=locations,
        #     )


    # User reached route via GET (as by clicking a link or via redirect)
    else:
        current_location = locations[1]
        current = current_location["location"]
        current_lat = current_location["lat"]
        current_long = current_location["long"]

        for destination in destinations:
            lat = destination["lat"]
            long = destination["long"]
            distance = round(haversine(current_long, current_lat, long, lat))
            distance = {"distance": distance}
            destination.update(distance)

        return render_template(
            "index.html",
            current=current,
            destinations=destinations,
            locations=locations,
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


def errorhandler(e):
    """Handle error"""
    if not isinstance(e, HTTPException):
        e = InternalServerError()
    return apology(e.name, e.code)


# Listen for errors
for code in default_exceptions:
    app.errorhandler(code)(errorhandler)
