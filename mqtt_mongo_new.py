#Website connect to Mongodb with MQTT

import paho.mqtt.client as mqtt
import _thread
import time
import os
import pymongo
from pymongo import MongoClient

# message format: 'Temperature:23.56 / Humidity:55.78 / Light:50000 / UV:53.54 / Soil:534.12 / Pressure:1012.15'

def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))

	# Subscribing in on_connect() means that if we lose the connection and
	# reconnect then subscriptions will be renewed.
    client.subscribe("mqtt/data")
    client.subscribe("mqtt/web")
    client.subscribe("mqtt/test")

# The callback for when a PUBLISH message is received from the server.
def on_message(client, usrdata, msg):
    if msg.topic == "mqtt/test":
        print("Topic:" + msg.topic+" "+ "Message: " + str(msg.payload.decode("utf-8")))
    data = str(msg.payload.decode("utf-8"))
    if msg.topic == "mqtt/data":
        index_temp = data.find('Temperature')
        index_humid = data.find('Humidity')
        index_light = data.find('Light')
        index_uv = data.find('UV')
        index_soil = data.find('Soil')
        index_press = data.find('Pressure')
        
        insert_data = {"Temperature": data[12:17],
                       "Humidity":data[index_humid+9:index_humid+14],
                       "Light":data[index_light+6:index_light+11],
                       "UV":data[index_uv+3:index_uv+8],
                       "Soil":data[index_soil+5:index_soil+11],
                       "Pressure":data[index_press+9:index_press+16]
                       }
        collection.insert_one(insert_data)
    elif msg.topic == "mqtt/web":
        if data == "request":
            n = 0
            for da in collection.find().sort('_id', pymongo.DESCENDING).limit(5):
                client.publish("mqtt/web", str(n) + str(da))
                n = n + 1
                time.sleep(0.5)

def publish(arg):
    while 1:
        msg = input("Please enter the message to publish: ")
        if msg == "":
            print("No input, program will end now...")
            client.loop_stop()
            client.unsubscribe("mqtt/data")
            client.unsubscribe("mqtt/web")
            client.disconnect()
            os._exit(1)
            break;
        else:
            client.publish("mqtt/test", msg)
            time.sleep(0.5)

# Mongo Part
mongo_client = MongoClient()
db = mongo_client.IOT
collection = db.sensor_data

# MQTT Part
client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message
client.connect("140.116.82.42")

client.loop_start()

_thread.start_new_thread(publish, ("arg",))

while 1:
    pass
