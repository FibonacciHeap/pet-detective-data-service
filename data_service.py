# import httplib
import hashlib
import mimetypes
import hmac
import base64
from email.utils import formatdate
import sys
import os

import json
from flask import Flask, request, jsonify
app = Flask(__name__)

# Environment variables are defined in app.yaml.
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ['SQLALCHEMY_DATABASE_URI']
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)


class Report(db.Model):
    userId = db.Column(db.String(46), primary_key=True)
    reportTime = db.Column(db.DateTime())
    name = db.Column(db.String(46))
    reportType = db.Column(db.String)


    def __init__(self, timestamp, user_ip):
        self.timestamp = timestamp
        self.user_ip = user_ip


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
#			"reportTime", time.now, 
#           "name", "Will Smith",
#           "reportType", "samaratin",
#           "reportLocation", [123.3234,23.6543]
#           "url", "http://google.com"
#           "color", "#3a346e",
#           "incidentLocation", 94706,
#           "petType", "dog",
#           "breed", "pug",
#           "found", true, 
#           "rejections", [122,653],
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
def post_lost_pet():
    data = request.data
    if type(data) == str:
        data = json.loads(data)
    image_url = data["url"]



    # if new_metadata:
    #     status, body = send_custom_query(ACCESS_KEY, SECRET_KEY, target_id, new_metadata)
    #     return body, status
    # else:
#     #     return 'No new metadata passed', 400


@app.route("/found", methods=['POST'])
def post_found_pet():
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



