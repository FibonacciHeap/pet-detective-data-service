import httplib
import hashlib
import mimetypes
import hmac
import base64
from email.utils import formatdate
import sys
import os
import json
import threading

from google.cloud import datastore
from flask import Flask, request, jsonify, current_app
app = Flask(__name__)



def get_client():
    return datastore.Client(current_app.config['PROJECT_ID'])


# [START from_datastore]
def from_datastore(entity):
    """Translates Datastore results into the format expected by the
    application.

    Datastore typically returns:
        [Entity{key: (kind, id), prop: val, ...}]

    This returns:
        {id: id, prop: val, ...}
    """
    if not entity:
        return None
    if isinstance(entity, builtin_list):
        entity = entity.pop()

    entity['id'] = entity.key.id
    return entity
# [END from_datastore]



# analytics query servicing
@app.route("/analytics", methods=['GET'])
def post_found_pet():
    key = client.key('Task')
    report = datastore.Entity(key)



# consuming the CV API
def getRecognitionData(url):
	############# TESTING ONLY #############
	return 200, jsonify({"petType", "dog"}) 
    ########################################

    # http_method = 'GET'
    # date = formatdate(None, localtime=False, usegmt=True)

    # endpoint = "ENDPOINT_NOT_DEFINED"
    # path = "/recognize/?url=" + url
    # content_type_bare = 'application/json'

    # # Sign the request and get the Authorization header
    # # auth_header = authorization_header_for_request(access_key, secret_key, http_method, request_body, content_type_bare,
    #                                                # date, path)
    # request_headers = {
    #     'Accept': 'application/json',
    #     'Authorization': auth_header,
    #     'Content-Type': content_type_bare,
    #     'Date': date
    # }

    # # Make the request over HTTPS on port 443
    # http = httplib.HTTPSConnection(endpoint, 443)
    # http.request(http_method, path, request_body, request_headers)

    # response = http.getresponse()
    # response_body = response.read()
    # return response.status, response_body


# push to the database for lost pets
@app.route("/lost", methods=['POST'])
def post_lost_pet():
	key = client.key('Task')
    report = datastore.Entity(key)

	data = request.data # get the header body
    if type(data) == str:
        data = json.loads(data)[0] # convert to dictionary
    url = data["url"]
    status, classification = getRecognitionData(url)

    if (status != 200) {
    	print("Error: ", status)
    	return status
    }

    statusUpdate = [] # {"caregiverLocation": 0, "caregiverID": "", "caregiverName": "", "time": datetime.datetime.utcnow()}
    data["status"] = statusUpdate # add initial status
    data["reportType"] = "owner"
    data["found"] = false
    data["rejections"] = []

    data["petType"] = classification["petType"]
    data["color"] = classification["color"]
	report.update(data)
	thr = threading.Thread(target=client.put, args=(report), kwargs={})
    thr.start()

    # Acknowledge that data is being posted
    return jsonify({}), 200


# push to the database for found pets
@app.route("/found", methods=['POST'])
def post_found_pet():
    key = client.key('Task')
    report = datastore.Entity(key)

	data = request.data # get the header body
    if type(data) == str:
        data = json.loads(data)[0] # convert to dictionary

    url = data["url"]
    status, classification = getRecognitionData(url)

    if (status != 200) {
    	print("Error: ", status)
    	return status
    }

    statusUpdate = [{"caregiverLocation": 0, "caregiverID": "", "caregiverName": "", "time": datetime.datetime.utcnow()}]
    data["status"] = statusUpdate # add initial status
    data["reportType"] = "owner"
    data["found"] = false
    data["rejections"] = []

    data["petType"] = classification["petType"]
    data["color"] = classification["color"]

	report.update(data)
	thr = threading.Thread(target=client.put, args=(report), kwargs={})
    thr.start()

    # Acknowledge that data is being posted
    return jsonify({}), 200


@app.route("/")
@app.route("/index")
def index():
    return "Index page"

if __name__ == "__main__":
    app.run(debug=True)


#  Request Format
#
#   Verb: POST
#   Request Body Example:
#       {
#			"reportID", 12345,
#			"reportLocation", [123.3234,23.6543],
#			"reportType", "samaratin",
#           "userID": "123",
#			"reportTime", time.now, 
#           "userName", "Will Smith",
#           "reportType", "samaratin",
#           "reportLocation", [123.3234,23.6543]
#           "url", "http://google.com"
#           "color", "#3a346e",
#           "incidentLocation", 94706,
#           "petType", "dog",
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

