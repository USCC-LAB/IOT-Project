import pymongo
from pymongo import MongoClient
from bson.objectid import ObjectId

mongo_client = MongoClient()
db = mongo_client.IOT
collection = db.sensor_data

for data in collection.find({"_id": {"$gt":ObjectId("5b6db6800000000000000000"), "$lt":ObjectId("5b6ea5900000000000000000")}}):
        #print(type(data["Temperature"]))
    print(data["Pressure"], end = " ")
    print(data["Pressure"].replace("/", ""))
    
    myquery = {"_id":data["_id"]}
    newValue = {"$set": {"Temperature": data["Temperature"].replace("/", ""),"Humidity": data["Humidity"].replace("/", ""), "Light": data["Light"].replace("/", ""), "UV": data["UV"].replace("/", ""), "Soil": data["Soil"].replace("/", ""), "Pressure": data["Soil"].replace("/", "")}}
    collection.update_one(myquery, newValue)
    pass
