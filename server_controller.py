import paho.mqtt.client as mqtt 
import time
import _thread
import os
from datetime import datetime


# will be closed at another thread (.close())
# 3rd argument indicates no. of lines to buffer
# set to 1 so the buffer will flush in this case
log_file = open("on_off.log", "a+", 1)
log_time = open("timer.log", "a+", 1)
log_temp = open("temp.log", "a+", 1)
log_humi = open("humid.log", "a+", 1)
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

def get_schedule_str():
    # f1 = open('timer.log')
    # f2 = open('temp.log')
    # f3 = open('humid.log')
    # line_list1 = f1.readlines()
    # line_list2 = f2.readlines()
    # line_list3 = f3.readlines()
    # schedule_str = line_list1[-1] + " " + line_list2[-1] + " " + line_list3[-1] + " "
    f = open("schedule.log")
    line_list = f.readlines()[-1]
    print(line_list)
    return line_list

def get_status_str():
    f = open('on_off.log')
    line_list = f.readlines()
    # print(line_list[-1])
    if "ON" in line_list[-1]: 
        return "ON"
    else:
        return "OFF"


def on_message(client, userdata, message):
    msg = str(message.payload.decode("utf-8"))

    if message.topic == "mqtt/control" and (msg == "ON" or msg == "OFF"):
        log_file.write(get_time_str() + msg + "\n")
        client.publish("mqtt/control", "server_" + get_status_str())

    elif message.topic == "mqtt/control" and msg == "ACK":
        get_schedule_str()
        client.publish("mqtt/control", "server_" + get_status_str())
        client.publish("mqtt/schedule", "server_" + get_schedule_str())
    
    elif message.topic == "mqtt/schedule" and msg[0:6] != "server":
        ch = log_sche.write("\n" + msg)
        if ch != 0:
            print("File write success")
        client.publish("mqtt/schedule", "server_" + get_schedule_str())
        
    print("Topic : " + message.topic + " || Message : " + msg + "\n")

    

def publish(lol):
    while 1:
        line = input("Please enter the message to publish : ")
        if line == "":
            print("No input, program will end now ...")
            client.loop_stop()  # stop the loop
            client.unsubscribe("mqtt/control")
            client.unsubscribe("mqtt/data")
            client.unsubscribe("mqtt/schedule")
            client.disconnect()
            log_file.close()
            os._exit(1)
            break
        else:
            client.publish(topic, line)
            time.sleep(0.5)



#mongodb part
# mg_client = MongoClient()
# db = mg_client.IOT
# posts = db.sensor_data

broker_address = input("Enter the broker ip(leave blank for default): ")
if broker_address == "":
    broker_address = "140.116.82.42" # default

# we need all together 3 instance
# add later
client = mqtt.Client("P1") 
client.on_message = on_message # attach function to callback
client.connect(broker_address) # connect to broker

topic = input("Enter the topic(leave blank for default):")
if topic == "":
    topic = "mqtt/control"


client.loop_start() # start the loop
print("Subscribing to topic : " + topic)

client.subscribe("mqtt/control")
client.subscribe("mqtt/schedule")
print("Subscribing to mqtt/data to receive sensor info")
client.subscribe("mqtt/data")

# start a new thread to pending user input and publish
_thread.start_new_thread(publish, ("lol",))  # format: start_new_thread(function_name ,("args","second args"))

while 1:
    # time.sleep(1)
    # t = datetime.now()
    # log_file.write("[" + str(t.year)[2:4] + "-" + str(t.month) + "-" + str(t.day) + "]")
    # log_file.write(str(t.hour) + ":" + str(t.minute) + ":" + str(t.second) + "~\n")
    pass
    
