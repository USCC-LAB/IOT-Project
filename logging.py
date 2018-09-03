import paho.mqtt.client as mqtt 
import time
import _thread
import os
from datetime import datetime


# will be closed at another thread (.close())
# 3rd argument indicates no. of lines to buffer
# set to 1 so the buffer will flush in this case
log_file = open("on_off.log", "a+", 1)
log_sche = open("schedule.log", "a+", 1)


def chg_str(value):
    if value < 10:
	    return "0" + str(value)
    else:
        return str(value)


def get_time_str():
    t = datetime.now()
    time_str = "[" + str(t.year)[2:4] + "-" + chg_str(t.month) + "-" + chg_str(t.day) + "] "
    time_str = time_str + chg_str(t.hour) + ":" + chg_str(t.minute) + ":" + chg_str(t.second) + " ~ "
    return time_str


def on_message(client, userdata, message):
    msg = str(message.payload.decode("utf-8"))

    if "control" in message.topic:
        log_file.write(get_time_str() + msg + "\n")

    elif "schedule" in message.topic:
        log_sche.write(msg+"\n") 
    

def publish(lol):
    while 1:
        line = input("Please enter the message to publish : ")
        if line == "":
            print("No input, program will end now ...")
            client.loop_stop()  # stop the loop
            client.unsubscribe("uscclab/#")
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

client = mqtt.Client("Server Client") 
client.username_pw_set("weblogin", "wtf123")
client.on_message = on_message # attach function to callback
client.connect(broker_address) # connect to broker

client.loop_start() # start the loop
client.subscribe("uscclab/#")

# start a new thread to pending user input and publish
_thread.start_new_thread(publish, ("lol",))  # format: start_new_thread(function_name ,("args","second args"))

while 1:
    pass
    
