#Website connect to Mongodb with MQTT

import paho.mqtt.client as mqtt
import _thread
import time
import os
import pymongo
import numpy as np
from pymongo import MongoClient
from bson.objectid import ObjectId

# message format: 'Temperature:23.56 / Humidity:55.78 / Light:50000 / UV:53.54 / Soil:534.12 / Pressure:1012.15'

log_file = open("on_off.log", "a+", 1)

def chg_str(value):
    if value < 10:
        return "0" + str(value)
    else:
        return str(value)


def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))

	# Subscribing in on_connect() means that if we lose the connection and
	# reconnect then subscriptions will be renewed.
    client.subscribe("mqtt/data")
    client.subscribe("mqtt/web")
    client.subscribe("mqtt/test")
    client.subscribe("mqtt/dashboard")

# The callback for when a PUBLISH message is received from the server.
def on_message(client, usrdata, msg):
        #if msg.topic == "mqtt/test":
    #print("Topic:" + msg.topic+" "+ "Message: " + str(msg.payload.decode("utf-8")))
    data = str(msg.payload.decode("utf-8"))
    
    if msg.topic == "mqtt/data":
        '''index_temp = data.find('Temperature')
        index_humid = data.find('Humidity')
        index_light = data.find('Light')
        index_uv = data.find('UV')
        index_soil = data.find('Soil')
        index_press = data.find('Pressure')
        index_time = data.find('Time')
        
        insert_data = {"Temperature": data[index_temp+12:index_temp+16],
                       "Humidity":data[index_humid+9:index_humid+14],
                       "Light":data[index_light+6:index_light+13],
                       "UV":data[index_uv+3:index_uv+9],
                       "Soil":data[index_soil+5:index_soil+11],
                       "Pressure":data[index_press+9:index_press+17],
                       "Time":data[index_time+10:index_time+24]
                       }'''
        temp = slice_data("Temperature", data)
        humid = slice_data("Humidity", data)
        light = slice_data("Light", data)
        uv = slice_data("UV", data)
        soil = slice_data("Soil", data)
        press = slice_data("Pressure", data)
        time = slice_data("Time", data)

        insert_data = {"Temperature": temp,
                       "Humidity": humid,
                       "Light": light,
                       "UV": uv,
                       "Soil": soil,
                       "Pressure": press,
                       "Time": time
                       }
        print(insert_data)
        collection.insert_one(insert_data)

    elif msg.topic == "mqtt/web":
        # message format: request ooooo xxxxxxxxxxxxxxxxxxxxxxxx xxxxxxxxxxxxxxxxxxxxxxxx
        if data[0:7] == "request":
            #n = 0
            #for da in collection.find().sort('_id', pymongo.DESCENDING).limit(int(data[7:9])):
                #client.publish("mqtt/web", str(n) + str(da))
                #n = n + 1
                #time.sleep(0.1)
            
            db_data = []
            during = data[8:13]
            id1 = data[14:38]
            id2 = data[39:63]
            
            print("\nid1: "+id1)
            print("id2: "+id2)
            one = True
            #for da in collection.find({"_id": {"$gt": ObjectId(id1), "$lt": ObjectId(id2)}}):
            for da in collection.find({"_id": {"$gt": ObjectId(id1)}}):
                if da["_id"] >= ObjectId(id2):
                    break;
                if one == True:
                    one = False
                elif one == False:
                    db_data.append(da)
            
            if db_data == []:
                client.publish("mqtt/web", "no data")
            else:
                compute(during, db_data);
            
            # form_data fromat: "{Temperature:xx.xx / Humidity:xx.xx / ...} | {...} | {...}"
        elif data == "too early":
            client.publish("mqtt/web", "no data")

    elif msg.topic == "mqtt/dashboard":
        pass 
    elif msg.topic == "mqtt/control" and (data == "ON" or data == "OFF"):
        t = datetime.now()
			
        log_file.write("[" + str(t.year)[2:4] + "-" + chg_str(t.month) + "-" + chg_str(t.day) + "] ")
        log_file.write(chg_str(t.hour) + ":" + chg_str(t.minute) + ":" + chg_str(t.second) + " ~ ")
        log_file.write(msg + "\n")
        
    elif message.topic == "mqtt/control" and msg == "ACK":
        f = open('on_off.log')
        line_list = f.readlines()
        # print(line_list[-1])
        if "ON" in line_list[-1]: 
            print("ON")
        else:
            print("OFF")
    
def slice_data(dt_type, toslice):
    toslice = toslice[toslice.find(dt_type):]
    slash = toslice.find("/")
    data = toslice[slash+2:]
    print(data)

    if dt_type == "Temperature":
        return toslice[12 : slash-1]
    elif dt_type == "Humidity":
        return toslice[9 : slash-1]
    elif dt_type == "Light":
        return toslice[6 : slash-1]
    elif dt_type == "UV":
        return toslice[3 : slash-1]
    elif dt_type == "Soil":
        return toslice[5 : slash-1]
    elif dt_type == "Pressure":
        return toslice[9 : slash-1]
    elif dt_type == "Time":
        return toslice[5 :]

def compute(during, data_dic):
    #print(type(data_str[0]['_id']))
    base = []
    date = ""
    co = 0
    #print(data_dic)
    for one_dic in data_dic:
        co += 1
            #print("one_dic start", end = " ")
        if during == "month":
            if one_dic["Time"][0:3] == "201":
                if date != one_dic["Time"][5:10]:
                    date = one_dic["Time"][5:10]
            elif one_dic["Time"][2] == "-":
                if date != one_dic["Time"][0:5]:
                    date = one_dic["Time"][0:5]
            if date == "":
                continue
            try:
                one = [float(one_dic["Temperature"]), float(one_dic["Humidity"]), float(one_dic["Light"]), float(one_dic["UV"]), float(one_dic["Soil"]), float(one_dic["Pressure"]), int(date[0:2]+date[3:5])]
            except:
                continue
            else:
                #print(one)
                base.append(one)
        elif during == " week":
            if one_dic["Time"][0:3] == "201":
                if date != one_dic["Time"][5:10]:
                    date = one_dic["Time"][5:10]
            elif one_dic["Time"][2] == "-":
                if date != one_dic["Time"][0:5]:
                    date = one_dic["Time"][0:5]
            if date == "":
                continue
            try:
                one = [float(one_dic["Temperature"]), float(one_dic["Humidity"]), float(one_dic["Light"]), float(one_dic["UV"]), float(one_dic["Soil"]), float(one_dic["Pressure"]), int(date[0:2]+date[3:5])]
            except:
                continue
            else:
                #print(one)
                base.append(one)
        elif during == "  day":
            if one_dic["Time"][0:3] == "201":
                if date != one_dic["Time"][11:13]:
                    date = one_dic["Time"][11:13]
            elif one_dic["Time"][2] == "-":
                if date != one_dic["Time"][6:8]:
                    date = one_dic["Time"][6:8]
            if date == "":
                continue
            try:
                one = [float(one_dic["Temperature"]), float(one_dic["Humidity"]), float(one_dic["Light"]), float(one_dic["UV"]), float(one_dic["Soil"]), float(one_dic["Pressure"]), int(date)]
            except Exception as e:
                    #print(co, end = " ")
                    #print("err:", end = "")
                #print(e, end = " ")
                continue
            else:
                    #print(co, end = " ")
                #print("print one[6]:", end = "")
                #print(one[6])
                base.append(one)
    #print(base)
    try:
        oneday = base[0][6]
    except:
        print("illegal operation")
    else:
        mean_base = []
        mean_list = []
        first = True
        count = 0;
        for i in base:
            if i[6] != oneday or count == len(base)-1:
                oneday = i[6]
                mean_arr = np.array(mean_list)
                mean_arr = np.mean(mean_arr, 0)
                mean_list = mean_arr.tolist()
                mean_base.append(mean_list)
                mean_list = []
            mean_list.append(i)
            count += 1
    
        print("mean")
        print(mean_base)
        client.publish("mqtt/web", str(mean_base))


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
            break
        else:
            client.publish("mqtt/test", msg)
            time.sleep(0.5)

# Mongo Part
mongo_client = MongoClient()
db = mongo_client.IOT
collection = db.sensor_data

# MQTT Part
client = mqtt.Client()
client.username_pw_set("weblogin", "wtf123")
client.on_connect = on_connect
client.on_message = on_message
client.connect("140.116.82.42")

client.loop_start()

_thread.start_new_thread(publish, ("arg",))

while 1:
    pass
