import pandas as pd
import numpy as np
import itertools
from datetime import datetime,timedelta
from pymongo import MongoClient
import threading
import re
import time
import bson
import warnings
from Geolocation import GeoLocation

client = ""
db =""
model_nn =""
REFRESH_TIME = 30 #in minutes
def initialize():
	global model_nn,client,db
	# model_nn = load_model('model_nn_corrected.h5py')
	url="mongodb+srv://dbuser:dbuser@cluster0-cw2oj.mongodb.net/test?retryWrites=true&w=majority"
	client=MongoClient(url)
	db = client.Pothole_Details
	warnings.simplefilter("ignore")
	# refreshPotholeInformation()


def storePoints(locationList):
	collection = db.Pothole_Holder
	for location in locationList:
		loc = {
			"longitude":location[1],
			"latitude":location[0],
			"time": datetime.now().strftime("%d-%m-%Y %H:%M:%S")
		}
		collection.insert_one(loc)

def refreshPotholeInformation():
	pothole = db.Pothole_Information
	holding = db.Pothole_Holder
	nowTime = datetime.now().strftime("%d-%m-%Y %H:%M:%S")
	start = time.perf_counter()

	points = holding.aggregate([
		{"$group" : {"_id":{"longitude" : "$longitude","latitude" : "$latitude"},"count":{"$sum":1},"time":{"$first": "$time"}}},
		{"$project" : {"longitude":"$_id.longitude","latitude":"$_id.latitude","count":1,"_id":0,"time":1}}
	])
	res = [i for i in points]
	
	for p in res:
		res = pothole.find({"latitude":p["latitude"],"longitude":p["longitude"]})
		res = [i for i in res]
		if len(res) > 0:
			pothole.update_one({"latitude":p["latitude"],"longitude":p["longitude"]},{
				"$set" :{"last report":p["time"]},
				"$push" : {"reports": {"time":nowTime,"count":p["count"]}},
				"$inc" : {"reportCount":p["count"]}
			})
		else:
			pothole.insert_one({
				"Time of First report" : p["time"],
				"longitude":p["longitude"],
				"latitude":p["latitude"],
				"reports":[{"time":nowTime,"count":p["count"]}],
				"reportCount":p["count"],
				"last report":p["time"]
			})
	holding.delete_many({})
	end = time.perf_counter()
	threading.Timer(REFRESH_TIME * 60 - (end - start), refreshPotholeInformation).start()

def getAllPointsReport(minLng, minLat, maxLng, maxLat):
	pothole = db.Pothole_Information
	holes = pothole.find({
		"latitude":{"$gt":minLat,"$lt":maxLat},
		"longitude":{"$gt":minLng,"$lt":maxLng},
	},{"_id":0})
	r = [i for i in holes]
	# print(r)
	return r

def getPotholes(latitude, longitude, radius,day):
	#Radius in KMs
	min,max = GeoLocation.from_degrees(latitude,longitude).bounding_locations(radius)
	pothole = db.Pothole_Information
	lastdate = datetime.now() - timedelta(day)
	lastdate = lastdate.__str__()
	res = pothole.find({
		"latitude":{"$gt":min.deg_lat,"$lt":max.deg_lat},
		"longitude":{"$gt":min.deg_lon,"$lt":max.deg_lon},
		"last report":{"$gt":lastdate}
	},
	{"_id":0,"reports":0,"Time of First report":0})
	r = [i for i in res]
	# print(r)
	return r