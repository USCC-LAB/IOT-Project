import paho.mqtt.client as mqtt
import time
import _thread
import os

# This is python mqtt client for sensor node
# To use this python script please run the following command first
#         pip3 install paho-mqtt
# To run this program
#         python3 mqtt_sensor.py

# To do : 1.change the instance name for each node


def on_message(client, userdata, message):
    print("\n" + str(message.payload.decode("utf-8") + " (" + message.topic + ")") + "\n")


# This is the public function, attach the data to the string variable here
def publish(name):
    while 1:
        line = name + ": " + input("Please enter message: ")
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


# Modify the broker ip here, default will be uscclab server
broker_address = "140.116.82.42"

# create new instance , change the instance name here to avoid crash
print("creating new instance")
instance = "Node 1"
client = mqtt.Client(instance)
client.on_message = on_message

print("connecting to broker")
client.connect(broker_address) # connect to broker

# Enter the topic to subscribe here, web default is "mqtt/demo"
topic = "mqtt/demo"
client.loop_start()  # start the loop
print("Subscribing to topic : " + topic)
client.subscribe(topic)


# start a new thread to pending user input and publish
_thread.start_new_thread(publish, (instance,))  # format: start_new_thread(function_name ,("args","second args"))

while 1:  # to let the main thread running in the background
    pass


