# import httplib2
import hashlib
import mimetypes
import hmac
import base64
import time
from email.utils import formatdate
import sys
import os
import json
import threading
from multiprocessing.dummy import Pool
from google.cloud import datastore
from flask import Flask, request, jsonify, current_app, redirect


app = Flask(__name__)
pool = Pool(processes=1)

def get_client():
    return datastore.Client()


# analytics query servicing
@app.route("/analytics", methods=['GET'])
def getAnalytics():
    key = client.key('Task')
    report = datastore.Entity(key)



# consuming the CV API
def getRecognitionData(url, data, senderType):
    # ############# TESTING ONLY #############
    # return {"petType": "dog"}, 200
 #    ########################################
    http_method = 'GET'
    client = get_client()
    key = client.key('userID', data['userID'])
    report = datastore.Entity(key)

    content_type_bare = 'application/json'
    date = formatdate(None, localtime=False, usegmt=True)
    endpointCV = "https://cv-dot-pet-detective-159121.appspot.com"
    pathCV = "/recognize/?url=" + url

    # Sign the request and get the Authorization header
    auth_header = authorization_header_for_request(access_key, secret_key,
        http_method, request_body, content_type_bare, date, pathCV)
    request_headers = {
        'Accept': 'application/json',
        'Authorization': auth_header,
        'Content-Type': content_type_bare,
        'Date': date
    }

    # Make the request over HTTPS on port 443 to CV API
    http = httplib.HTTPSConnection(endpointCV, 443)
    http.request(http_method, pathCV, request_body, request_headers)
    response = http.getresponse()
    response_body = response.read()

    statusUpdate = [] # {"caregiverLocation": 0, "caregiverID": "", "caregiverName": "", "time": datetime.datetime.utcnow()}
    data["reportID"] = key
    data["status"] = statusUpdate # add initial status
    data["reportType"] = senderType # owner or samaratin
    data["found"] = False
    data["rejections"] = []
    data["petType"] = response_body["petType"]
    data["color"] = response_body["color"]

    report.update(data)
    report["userID"] = "456"
    time.sleep(5)
    client.put(report)

    # Make the request over HTTPS on port 443 to MS API
    date = formatdate(None, localtime=False, usegmt=True)
    endpointMS = "https://endpointnotdefined.com" #https://match-dot-pet-detective-159121.appspot.com/
    pathMS = "/recognize/?url=" + url

    # Sign the request and get the Authorization header
    auth_header = authorization_header_for_request(access_key, secret_key,
        http_method, request_body, content_type_bare, date, pathMS)

    http = httplib.HTTPSConnection(endpointMS, 443)
    http.request(http_method, pathMS, request_body, request_headers)
    response = http.getresponse()
    response_body = response.read()

    return {}, response.status

def recognitionDataCallback():
    print("Returned from asynch function")


# push to the database for lost pets
@app.route("/lost", methods=['POST'])
def post_lost_pet():

    # data = {
    #     "reportID": 12345,
    #     "reportLocation": [123.3234,23.6543],
    #     "reportType": "samaratin",
    #     "userID": "123",
    #     "reportTime": time.time(), 
    #     "userName": "Will Smith",
    #     "reportType": "samaratin",
    #     "reportLocation": [123.3234,23.6543],
    #     "url": "http://google.com",
    #     "incidentLocation": 94706
    # }

    data = request.data # get the header body

    if type(data) == str:
        data = json.loads(data)[0] # convert to dictionary
    url = data["url"]

    newCallbackFunction = lambda new_name: recognitionDataCallback(url, data, "owner")
    pool.apply_async(getRecognitionData, args=[url,data], callback=newCallbackFunction)
    # return {}, 200
    return redirect('/')


# push to the database for found pets
@app.route("/found", methods=['POST'])
def post_found_pet():
    
    # data = {
    #     "reportID": 12345,
    #     "reportLocation": [123.3234,23.6543],
    #     "reportType": "samaratin",
    #     "userID": "123",
    #     "reportTime": time.time(), 
    #     "userName": "Will Smith",
    #     "reportType": "samaratin",
    #     "reportLocation": [123.3234,23.6543],
    #     "url": "http://google.com",
    #     "incidentLocation": 94706
    # }

    data = request.data # get the header body

    if type(data) == str:
        data = json.loads(data)[0] # convert to dictionary
    url = data["url"]

    newCallbackFunction = lambda new_name: recognitionDataCallback(url, data, "samaratin")
    pool.apply_async(recognitionDataCallback, args=[url,data], callback=newCallbackFunction)
    # return {}, 200
    return redirect('/')


@app.route("/")
@app.route("/index")
def index():
    return "Index page"

if __name__ == "__main__":
    app.run(debug=True)



 
#           "color", "#3a346e",
          
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




#  Request Format
#
#   Verb: POST
#   Request Body Example:
#       {
#           "reportID", 12345,
#           "reportLocation", [123.3234,23.6543],
#           "reportType", "samaratin",
#           "userID": "123",
#           "reportTime", time.now, 
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

