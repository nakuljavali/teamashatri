# app.py
from flask import Flask, request, jsonify, redirect
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
    headers = {"Authorization": "Bearer {}".format(req["access_token"])}
    # After 15th Feb (Unix Time)
    params = {"after": 1612975348}
    reqActivities = requests.get(url, headers = headers, params = params).json()
    resp = {}
    for activities in reqActivities:
        resp[activities["name"]] = activities["distance"]
    return 'Hello, ' + req["athlete"]["firstname"] + '\n.....You have done: ' + json.dumps(resp, separators=(',', ':'))  + ' since Feb 15'

if __name__ == '__main__':
    # Threaded option to enable multiple instances for multiple user access support
    app.run(threaded=True, port=5000)
