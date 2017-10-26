import paho.mqtt.client as mqtt 
import time
import _thread
import os
import pymongo
from pymongo import MongoClient

def on_message(client, userdata, message):
    print("Topic : " + message.topic + "|| Message : " + str(message.payload.decode("utf-8")) + "\n")
    post = {"text":str(message.payload.decode("utf-8"))}

    post_id = posts.insert_one(post).inserted_id


def publish(lol):
    while 1:
        line = input("Please enter the message to publish : ")
        if line == "":
            print("No input, program will end now ...")
            client.loop_stop()  # stop the loop
            client.unsubscribe(topic)
            client.disconnect()
            os._exit(1)
            break
        else:
            client.publish(topic, line)
            time.sleep(0.5)

#mongodb part
client = MongoClient()
db = client.test
posts = db.posts
# broker_address="192.168.1.184"  #enter ip here for local broker
broker_address = "140.116.82.42"  # public broker

print("creating new instance")
client = mqtt.Client("P2") # create new instance , change the instance name here to avoid crash
client.on_message = on_message # attach function to callback

print("connecting to broker")
client.connect(broker_address) # connect to broker

topic = "mqtt/demo"
client.loop_start() # start the loop
print("Subscribing to topic : " + topic)
client.subscribe(topic)

count = 0

# start a new thread to pending user input and publish
_thread.start_new_thread(publish, ("lol",))  # format: start_new_thread(function_name ,("args","second args"))

while 1: # to let the main thread running in the background
    pass


