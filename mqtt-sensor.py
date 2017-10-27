import time

import Adafruit_GPIO.SPI as SPI
import Adafruit_SSD1306

import Adafruit_DHT

from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont

import subprocess

import paho.mqtt.client as mqtt
import thread
import os


def on_message(client, userdata, message):
	print(str(message.payload.decode("utf-8") + " (" + message.topic + ")"))		

# Raspberry Pi pin configuration:
RST = None     # on the PiOLED this pin isnt used
# Note the following are only used with SPI:
DC = 23
SPI_PORT = 0
SPI_DEVICE = 0

# 128x64 display with hardware I2C:
disp = Adafruit_SSD1306.SSD1306_128_64(rst=RST)

# Initialize library.
disp.begin()

# Clear display.
disp.clear()
disp.display()

# Create blank image for drawing.
# Make sure to create image with mode '1' for 1-bit color.
width = disp.width
height = disp.height
image = Image.new('1', (width, height))

# Get drawing object to draw on image.
draw = ImageDraw.Draw(image)

# Draw a black filled box to clear the image.
draw.rectangle((0,0,width,height), outline=0, fill=0)

# Draw some shapes.
# First define some constants to allow easy resizing of shapes.
padding = -2
top = padding
bottom = height-padding

# Move left to right keeping track of the current x position for drawing shapes.
x = 0

# Load default font.
font = ImageFont.load_default()

font = ImageFont.truetype('Montserrat-Light.ttf', 12)
font2 = ImageFont.truetype('fontawesome-webfont.ttf', 14)
font_icon_big = ImageFont.truetype('fontawesome-webfont.ttf', 20)
font_text_big = ImageFont.truetype('Montserrat-Medium.ttf', 19)

# Sensor should be set to Adafruit_DHT.DHT11,
# Adafruit_DHT.DHT22, or Adafruit_DHT.AM2302.
sensor = Adafruit_DHT.DHT22

# Example using a Raspberry Pi with DHT sensor
# connected to GPIO4
pin = '4'

# Note that sometimes you won't get a readin and
# the results will be null (because Linux can't
# guarantee the timing of calls to read the sensor).
# If this happens try again!
# Modify the broker ip here, default will be uscclab server
broker_address = "140.116.82.42"

# create new instance , change the instance name here to avoid crash
print("creating new instance")
instance = "module_001"
client = mqtt.Client(instance)
client.on_message = on_message

print("connecting to broker at " + broker_address)
client.connect(broker_address)  # connect to broker

# Enter the topic to subscribe here, web default is "mqtt/demo"
topic = "mqtt/demo"

client.loop_start()  # start the loop
print("Subscribing to topic : " + topic)
client.subscribe(topic)

while True:
    # Try to grab a sensor reading. Use the read_retry method which will retry up
    # to 15 times to get a sensor readinf (waiting 2 second between each retry).
    humidity, temperature = Adafruit_DHT.read_retry(sensor, pin)
    
    if humidity is not None and temperature is not None:
        print('Temperature={0:0.1f}*C Humidity={1:0.1f}%'.format(temperature,humidity))
    else:
        print(".")

    # Draw a black filled box to clear the image.
    draw.rectangle((0,0,width,height), outline=0, fill=0)

    # Shell scripts for system monitoring from here : 
    # https://unix.stackexchange.com/questions/119126/command-to-display-memory-usage-disk-usage-and-cpu-load
    cmd = "hostname -I | cut -d\' \' -f1 | head --bytes -1"
    IP = subprocess.check_output(cmd, shell = True )
    cmd = "top -bn1 | grep load | awk '{printf \"%.2f\", $(NF-2)}'"
    CPU = subprocess.check_output(cmd, shell = True )
    cmd = "free -m | awk 'NR==2{printf \"MEM: %.2f%%\", $3*100/$2 }'"
    MemUsage = subprocess.check_output(cmd, shell = True )
    
    line = instance + ' ' + IP + ' Temperature={0:0.1f}*C Humidity={1:0.1f}%'.format(temperature,humidity)
    client.publish(topic, line)

    # Icons
    draw.text((x, top),       unichr(61931),  font=font2, fill=255) #wifi icon
    draw.text((x, top+15),    unichr(62171),  font=font_icon_big, fill=255) #cpu icon
    
    draw.text((18, top),      str(IP),  font=font, fill=255) 
    draw.text((x+22, top+12), str(CPU), font=font_text_big, fill=255) 
    draw.text((x, top+36),    str(MemUsage),  font=font, fill=255)
        
    draw.text((x+80, top+36), '%0.1f'%humidity, font=font, fill = 255)
    draw.text((x+80, top+16), '%0.1f'%temperature, font=font, fill=255)
    
    # Display image.
    disp.image(image)
    disp.display()
    time.sleep(5)