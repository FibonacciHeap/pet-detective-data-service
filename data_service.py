# import httplib
import hashlib
import mimetypes
import hmac
import base64
from email.utils import formatdate
import sys
import os
import pyrebase

import json
from flask import Flask, request, jsonify
app = Flask(__name__)

config = {
    apiKey: "AIzaSyD-1U7VybKprHDVFLyuMEPVytBBLLDrmgE",
    authDomain: "petbot-af71f.firebaseapp.com",
    databaseURL: "https://petbot-af71f.firebaseio.com",
    storageBucket: "petbot-af71f.appspot.com"#,
    #messagingSenderId: "961663994191"
};

firebase = pyrebase.initialize_app(config)


# def send_custom_query(access_key, secret_key, target_id, new_metadata):
#     http_method = 'PUT'
#     date = formatdate(None, localtime=False, usegmt=True)

#     endpoint = "vws.vuforia.com"
#     path = "/targets/" + target_id

#     request_body = '{"application_metadata" : "' + new_metadata + '"}'
#     content_type_bare = 'application/json'

#     # Sign the request and get the Authorization header
#     auth_header = authorization_header_for_request(access_key, secret_key, http_method, request_body, content_type_bare,
#                                                    date, path)

#     request_headers = {
#         'Accept': 'application/json',
#         'Authorization': auth_header,
#         'Content-Type': content_type_bare,
#         'Date': date
#     }

#     # Make the request over HTTPS on port 443
#     http = httplib.HTTPSConnection(endpoint, 443)
#     http.request(http_method, path, request_body, request_headers)

#     response = http.getresponse()
#     response_body = response.read()
#     return response.status, response_body


#  Request Format
#
#   Verb: POST
#   Request Body Example:
#       {
#           "userID": "123", 
#           "name", "Will Smith",
#           "url", "http://google.com"
#           "color", "0x3a346e",
#           "incidentLocation", 94706,
#           "petType", "dog",
#           "breed", "pug",
#           "found", true, 
#           "status", [{
#                       "caregiverZip", 0,
#                       "caregiverID", ""
#                       "caregiverName", ""
#                       "time", 12389934852312
#                      }, 
#                      {
#                       "caregiverZip", 92831,
#                       "caregiverID", "12345"
#                       "caregiverName", "PetsRUs"
#                       "time", time.now
#                      }] 
#       }
#
#
#  Response Format
#
#   Successful Response Example:
#       Code: 200
#       Response Body: { <some json> }
#
#   Failure Response Example:
#       Code: 400
#       Response Body: " <some string explaining error> "




@app.route("/lost", methods=['POST'])
def def post_lost_pet():
    data = request.data
    if type(data) == str:
        data = json.loads(data)

    # if new_metadata:
    #     status, body = send_custom_query(ACCESS_KEY, SECRET_KEY, target_id, new_metadata)
    #     return body, status
    # else:
    #     return 'No new metadata passed', 400


@app.route("/found", methods=['POST'])
def def post_found_pet():
    data = request.data
    if type(data) == str:
        data = json.loads(data)
    target_id = data['id']
    new_metadata = base64.b64encode(data['metadata'])
    if new_metadata:
        status, body = send_custom_query(ACCESS_KEY, SECRET_KEY, target_id, new_metadata)
        return body, status
    else:
        return 'No new metadata passed', 400


@app.route("/")
@app.route("/index")
def index():
    return "Index page"

if __name__ == "__main__":
    app.run(debug=True)



