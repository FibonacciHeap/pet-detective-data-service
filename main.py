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
from math import sqrt
from multiprocessing.dummy import Pool
from google.cloud import datastore
from flask import Flask, request, jsonify, current_app, redirect


app = Flask(__name__)
pool = Pool(processes=1)

def get_client():
    return datastore.Client()


# analytics query servicing
def postAnalytics(recordType, newPost):
    http_method = 'POST'
    endpoint = "https://pd-match.herokuapp.com/match/check"
    content_type_bare = 'application/json'
    date = formatdate(None, localtime=False, usegmt=True)
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

    postType = newPost["reportType"]

    query = client.query(kind=recordType)
    query.add_filter('reportType', '!=', query)

    records = list(query.fetch(limit=1000))

    relevantRecords = []

    def euclidean_distance(x1,x2,y1,y2):
        return sqrt((x1-x2)**2 + (y1-y2)**2)

    for r in records:
        if euclidean_distance(newPost["reportLat"], r["reportLat"], newPost["reportLon"], r["reportLon"]) < 30:
            relevantRecords.add(r)

    queryResults = {"pet": newPost, "otherPets": relevantRecords}
    http.request(http_method, endpoint, queryResults, request_headers)


# consuming the CV API
def getRecognitionData(url, data, senderType):
    #return jsonify({"petType": "dog", "color": "#ffffff"}) # COMMENT ME OUT!!!

    http_method = 'GET'
    client = get_client()
    key = client.key(data['reportType'], data['userID'])
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

    postAnalytics(record["recordType"], report)
    print("Returned from analytics query.")
    return jsonify({})

def recognitionDataCallback():
    print("Returned from asynch function")


# push to the database for lost pets
@app.route("/lost", methods=['POST'])
def post_lost_pet():

    data = request.data # get the header body
    if (type(data) == bytes):
        data = json.loads(data.decode("utf-8"))

    print(data)
    print(type(data))

    #if type(data) == str:
    #    data = json.loads(user_data) # convert to dictionary
    url = data["url"]

    newCallbackFunction = lambda new_name: recognitionDataCallback(url, data, "owner")
    pool.apply_async(getRecognitionData, args=[url,data], callback=newCallbackFunction)
    return jsonify({})


# push to the database for found pets
@app.route("/found", methods=['POST'])
def post_found_pet():

    data = request.data # get the header body
    if (type(data) == bytes):
        data = json.loads(data.decode("utf-8"))

    print(data)
    print(type(data))

    #if type(data) == str:
    #    data = json.loads(user_data) # convert to dictionary
    url = data["url"]

    newCallbackFunction = lambda new_name: recognitionDataCallback(url, data, "samaratin")
    pool.apply_async(recognitionDataCallback, args=[url,data], callback=newCallbackFunction)



    return jsonify({})


@app.route("/")
@app.route("/index")
def index():
    return "Index page"

if __name__ == "__main__":
    app.run()



# data = {
    #     "reportLat": 123.3234,
    #     "reportLon": 23.6543,
    #     "reportType": "samaratin",
    #     "userID": "123",
    #     "reportTime": time.time(), 
    #     "userName": "Will Smith",
    #     "url": "http://google.com",
    #     "incidentLocation": 94706
    # }


 
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

