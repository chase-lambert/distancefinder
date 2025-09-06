import json
import os
import requests
import time
from datetime import datetime, timedelta

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

# Simple in-memory cache for geocoding results
geocoding_cache = {}
last_request_time = 0

# Geocoding service configuration (allows switching services)
GEOCODING_CONFIG = {
    'service': 'nominatim',  # Can be changed to switch services
    'nominatim_url': 'https://nominatim.openstreetmap.org/search',
    'backup_service': None  # Could be configured as fallback
}

def get_rate_limited_timestamp():
    """Ensure we don't exceed 1 request per second"""
    global last_request_time
    current_time = time.time()
    time_since_last = current_time - last_request_time
    
    if time_since_last < 1.0:
        sleep_time = 1.0 - time_since_last
        time.sleep(sleep_time)
    
    last_request_time = time.time()
    return last_request_time

def geocode_location(location_name):
    """
    Geocode a location with caching and rate limiting
    Returns (lat, lon) tuple or None if not found
    """
    # Check cache first
    cache_key = location_name.lower().strip()
    if cache_key in geocoding_cache:
        cached_result = geocoding_cache[cache_key]
        # Cache results for 24 hours
        if datetime.now() - cached_result['timestamp'] < timedelta(hours=24):
            return cached_result['coordinates']
    
    # Rate limit the request
    get_rate_limited_timestamp()
    
    try:
        if GEOCODING_CONFIG['service'] == 'nominatim':
            params = {
                'q': location_name,
                'format': 'json',
                'limit': 1,
                'email': 'your-email@example.com'  # Replace with your actual email
            }
            headers = {
                'User-Agent': 'Distance Finder App v1.0 (your-email@example.com)'
            }
            
            response = requests.get(
                GEOCODING_CONFIG['nominatim_url'], 
                params=params, 
                headers=headers, 
                timeout=10
            )
            response.raise_for_status()
            
            data = response.json()
            if data:
                lat = float(data[0]['lat'])
                lon = float(data[0]['lon'])
                
                # Cache the result
                geocoding_cache[cache_key] = {
                    'coordinates': (lat, lon),
                    'timestamp': datetime.now()
                }
                
                return (lat, lon)
        
    except Exception as e:
        print(f"Geocoding failed for {location_name}: {e}")
        
    return None

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
    destinations = [
        {'location': 'King, NC', 'lat': 36.30450135436856, 'long': -80.3242199}, 
        {'location': 'Dudley, NC', 'lat': 35.2673857, 'long': -78.0374891}, 
        {'location': 'Edinburgh, Scotland', 'lat': 55.9533456, 'long': -3.1883749}, 
        {'location': 'Medellin, Colombia', 'lat': 6.2443382, 'long': -75.573553}, 
        {'location': 'Redgranite, WI', 'lat': 44.0419238, 'long': -89.0984504}, 
        {'location': 'Marana, AZ', 'lat': 32.4446988, 'long': -111.2157091}, 
        {'location': 'Fairfield, CA', 'lat': 38.2493581, 'long': -122.039966}, 
        {'location': 'Yigo, Guam', 'lat': 13.535204499999999, 'long': 144.89715694673106}
    ]

    locations = [
        {'location': ""}, 
        {'location': 'Pilot Mountain', 'lat': 36.348500, 'long': -80.472361}, 
        {'location': 'King, NC', 'lat': 36.30450135436856, 'long': -80.3242199}, 
        {'location': 'Fort Payne, Alabama', 'lat': 34.4442547, 'long': -85.7196893}, 
        {'location': 'Hot Springs, Arkansas', 'lat': 34.5038393, 'long': -93.0552437}, 
        {'location': 'Canyon, Texas', 'lat': 34.99253385, 'long': -101.92788331921604}, 
        {'location': 'Pena Blanca, New Mexico', 'lat': 35.574754999999996, 'long': -106.33723818363845}, 
        {'location': 'Williams, AZ', 'lat': 35.2503394, 'long': -112.1869481}, 
        {'location': 'Springfield, Utah', 'lat': 37.1908427, 'long': -93.2932611}, 
        {'location': 'Torrey, Utah', 'lat': 38.2997368, 'long': -111.4204705}, 
        {'location': 'Moab, Utah', 'lat': 38.5738096, 'long': -109.5462146}, 
        {'location': 'Ashton, Idaho', 'lat': 44.071581, 'long': -111.448288}, 
        {'location': 'Browning, Montana', 'lat': 48.557743, 'long': -113.0172586}, 
        {'location': 'Custer, South Dakota', 'lat': 43.6726477, 'long': -103.5101597}, 
        {'location': 'Redgranite, WI', 'lat': 44.0419238, 'long': -89.0984504}, 
        {'location': 'Marana, AZ', 'lat': 32.4446988, 'long': -111.2157091}
    ]

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        current = locations[1]

        if request.form.get("location"):
            current = request.form.get("location")
            for location in locations:
                if location["location"] == current:
                    current_destination = location
                    break

            current_lat = current_destination["lat"]
            current_long = current_destination["long"]

            for destination in destinations:
                lat = destination["lat"]
                long = destination["long"]
                distance = round(haversine(current_long, current_lat, long, lat))
                destination["distance"] = distance

            return render_template(
                "index.html",
                current=current,
                destinations=destinations,
                locations=locations,
            )

        if request.form.get("new_location"):
            location_name = request.form.get("new_location")
            coordinates = geocode_location(location_name)
            
            if coordinates:
                current_lat, current_long = coordinates
                
                for destination in destinations:
                    lat = destination["lat"]
                    long = destination["long"]
                    distance = round(haversine(current_long, current_lat, long, lat))
                    destination["distance"] = distance

                return render_template(
                    "index.html",
                    current=location_name,
                    destinations=destinations,
                    locations=locations,
                )
            else:
                flash("Location not found. Please try a different location.")
                return render_template(
                    "index.html",
                    destinations=destinations,
                    locations=locations,
                )

    # User reached route via GET
    else:
        current_location = locations[2]
        current = current_location["location"]
        current_lat = current_location["lat"]
        current_long = current_location["long"]

        for destination in destinations:
            lat = destination["lat"]
            long = destination["long"]
            distance = round(haversine(current_long, current_lat, long, lat))
            destination["distance"] = distance

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
