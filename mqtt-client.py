import paho.mqtt.client as mqtt 
import time
import _thread
import os


def on_message(client, userdata, message):
    print("\nTopic : " + message.topic + "\n|| Message : " + str(message.payload.decode("utf-8")) + "\n")


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
            client.publish("mqtt/schedule", line, retain=True)
            time.sleep(0.5)


#Enter broker address
broker_address = input("Enter IP here: ")  

client = mqtt.Client("P3") # create new instance , change the instance name here for new client to avoid crash
client.username_pw_set("weblogin", "wtf123") # built-in function, first arg => username, second arg => password, comment this line to avoid password authentication
client.on_message = on_message # attach function to callback

print("connecting to broker")
client.connect(broker_address) # connect to broker

topic = "mqtt/control"
client.loop_start() # start the loop
print("Subscribing to topic : " + topic)
client.subscribe("mqtt/control")
client.subscribe("mqtt/schedule")

count = 0

# start a new thread to pending user input and publish
_thread.start_new_thread(publish, ("lol",))  # format: start_new_thread(function_name ,("args","second args"))

while 1:  # to let the main thread running in the background
    pass


