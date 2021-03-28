# app.py
from flask import Flask, request, jsonify, redirect, render_template
import requests
import json
import os

app = Flask(__name__)
base_url = "https://www.strava.com/api/v3/"
endpoint = "athlete/activities"
url = base_url + endpoint
client_id = os.getenv('CLIENT_ID')
client_secret = os.getenv('CLIENT_SECRET')
domain = os.getenv('DOMAIN')

# A welcome message to test our server
@app.route('/')
def index():
    request_uri = "https://www.strava.com/oauth/authorize?client_id={}&response_type=code&redirect_uri=http://{}/login/callback&approval_prompt=force&scope=read,activity:read".format(client_id, domain)
    return redirect(request_uri)

@app.route("/login/callback")
def callback():
    # Get authorization code Google sent back to you
    code = request.args.get("code")
    req = requests.post("https://www.strava.com/oauth/token?client_id={}&client_secret={}&code={}&grant_type=authorization_code".format(client_id, client_secret, code)).json()
    access_token = req['access_token']
    # After 15th Feb (Unix Time)
    params = {"after": 1613376000}
    category1 = "Run/Walk/Hike"
    category2 = "Ride"
    category3 = "Swim"
    resp = {"Run/Walk/Hike":0, "Ride":0, "Swim":0}

    page = 1
    while True:
        response = requests.get(url+ '?access_token=' + access_token + '&per_page=50' + '&page=' + str(page), params = params)
        reqActivities = response.json()
        if (not reqActivities):
            break
        for activities in reqActivities:
            if (activities["type"]=="Run" or activities["type"]=="Walk" or activities["type"]=="Hike"):
                resp[category1] += activities["distance"]*0.000621371192
            elif (activities["type"]=="Ride"):
                resp[category2] += activities["distance"]*0.000621371192
            elif (activities["type"]=="Swim"):
                resp[category3] += (activities["distance"]*0.000621371192)
        page += 1

    resp[category1] = round(resp[category1],2)
    resp[category2] = round(resp[category2],2)
    resp[category3] = round(resp[category3],2)

    return render_template('index.html', title='Asha Tri', user=req["athlete"]["firstname"], run=resp[category1],ride=resp[category2],swim=resp[category3])

if __name__ == '__main__':
    # Threaded option to enable multiple instances for multiple user access support
    app.run(threaded=True, port=5000)
