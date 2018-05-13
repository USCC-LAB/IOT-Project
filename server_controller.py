import paho.mqtt.client as mqtt 
import time
import _thread
import os
from datetime import datetime


# will be closed at another thread (.close())
# 3rd argument indicates no. of lines to buffer
# set to 1 so the buffer will flush in this case
log_file = open("test.txt", "a+", 1)


def on_message(client, userdata, message):
    msg = str(message.payload.decode("utf-8"))
    if message.topic == "mqtt/control" and (msg == "ON" or msg == "OFF"):
        t = datetime.now()
        log_file.write("[" + str(t.year)[2:4] + "-" + str(t.month) + "-" + str(t.day) + "]")
        log_file.write(str(t.hour) + ":" + str(t.minute) + ":" + str(t.second) + "~")
        log_file.write(msg + "\n")
    elif message.topic == "mqtt/control" and msg == "ACK":
        f = open('test.txt')
        line_list = f.readlines()
        # print(line_list[-1])
        if "ON" in line_list[-1]: 
            print("ON")
        else:
            print("OFF")
    
    print("Topic : " + message.topic + " || Message : " + msg + "\n")


def publish(lol):
    while 1:
        line = input("Please enter the message to publish : ")
        if line == "":
            print("No input, program will end now ...")
            client.loop_stop()  # stop the loop
            client.unsubscribe(topic)
            client.disconnect()
            log_file.close()
            os._exit(1)
            break
        else:
            client.publish(topic, line)
            time.sleep(0.5)


broker_address = input("Enter the broker ip(leave blank for default): ")
if broker_address == "":
    broker_address = "140.116.82.42" # default


# we need all together 3 instance
# add later
client = mqtt.Client("switch") 
client.on_message = on_message # attach function to callback
client.connect(broker_address) # connect to broker

topic = input("Enter the topic(leave blank for default):")
if topic == "":
    topic = "mqtt/control"


client.loop_start() # start the loop
print("Subscribing to topic : " + topic)
client.subscribe(topic)

# start a new thread to pending user input and publish
_thread.start_new_thread(publish, ("lol",))  # format: start_new_thread(function_name ,("args","second args"))

while 1:
    # time.sleep(1)
    # t = datetime.now()
    # log_file.write("[" + str(t.year)[2:4] + "-" + str(t.month) + "-" + str(t.day) + "]")
    # log_file.write(str(t.hour) + ":" + str(t.minute) + ":" + str(t.second) + "~\n")
    pass
    
