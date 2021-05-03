# Copyright 2021 Samim Konjicija
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

import time
import ntptime
from config import *
from machine import Pin, SoftSPI, SoftI2C, RTC, Timer, WDT
# sx127x library by lemariva from https://github.com/lemariva/uPyLoRaWAN
from sx127x import SX127x
if module_config['has_oled']==1:
# ssd1306 library by Adafruit from https://github.com/adafruit/micropython-adafruit-ssd1306
    from ssd1306 import SSD1306_I2C
import network
import webrepl
from umqtt.robust import MQTTClient
import ujson
import gc

# Timezone shift used in log entries
TZ=2

# Gateway version
GW_VER=0.6

# Encoding used
ENCODING='latin2'

# Logfile - logging module not used due to memory limitations on ESP8266
log = open("loragateway.log","a")

nic = network.WLAN(network.STA_IF)
time.sleep(1)
nic.active(True)
time.sleep(1)
nic.connect(wifi_config['ssid'], wifi_config['pwd'])

# Watchdog timer initialization
wdt = WDT()
logentry="Watchdog timer initialized."
logtime=time.localtime()
log.write("{}.{}.{} {}:{}:{} - {}\n".format(logtime[2],logtime[1],logtime[0],logtime[3]+TZ,logtime[4],logtime[5],logentry))

log.write("Connecting WiFi.\n")
while not nic.isconnected():
    print("Waiting to connect ...")
    wdt.feed()
    time.sleep(1)

if len(wifi_config['ip_addr'])==0:
    ipaddr=nic.ifconfig()[0]
else:
    nic.ifconfig((wifi_config['ip_addr'],wifi_config['ip_mask'],wifi_config['def_gw'],wifi_config['dns']))
    ipaddr=wifi_config['ip_addr']
logentry="Connected: {}\n".format(nic.ifconfig())
logtime=time.localtime()
log.write("{}.{}.{} {}:{}:{} - {}\n".format(logtime[2],logtime[1],logtime[0],logtime[3]+TZ,logtime[4],logtime[5],logentry))

print("Connected!")

webrepl.start()

# Updating clock from NTP server
# RTC not used due to memory limitations on ESP8266
ntptime.settime()
wdt.feed()

# For boards with OLED based on SSD1306
if module_config['has_oled']==1:
    logentry="Configuring OLED."
    logtime=time.localtime()
    log.write("{}.{}.{} {}:{}:{} - {}\n".format(logtime[2],logtime[1],logtime[0],logtime[3]+TZ,logtime[4],logtime[5],logentry))
    
    # configure OLED display
    oled_width = 128
    oled_height = 64
    # OLED reset pin
    i2c_rst = Pin(16, Pin.OUT)
    # Initialize the OLED display
    i2c_rst.value(0)
    time.sleep(0.010)
    i2c_rst.value(1) # must be held high after initialization
    # Setup the I2C lines
    i2c_scl = Pin(15, Pin.OUT, Pin.PULL_UP)
    i2c_sda = Pin(4, Pin.OUT, Pin.PULL_UP)
    # Create the bus object
    i2c = SoftI2C(scl=i2c_scl, sda=i2c_sda)
    # Create the display object
    oled = SSD1306_I2C(oled_width, oled_height, i2c)
    oled.fill(0)
    oled.text('Samim SmartHome', 0, 10)
    oled.text('LoRaMQTTGw '+str(GW_VER), 0, 20)
    oled.show()
    logentry="OLED configured"
    logtime=time.localtime()
    log.write("{}.{}.{} {}:{}:{} - {}\n".format(logtime[2],logtime[1],logtime[0],logtime[3]+TZ,logtime[4],logtime[5],logentry))

# Configure SX127x
if module_config['module_type']=='ESP32':
    logentry="Configuring ESP32."
    logtime=time.localtime()
    log.write("{}.{}.{} {}:{}:{} - {}\n".format(logtime[2],logtime[1],logtime[0],logtime[3]+TZ,logtime[4],logtime[5],logentry))
    device_spi = SoftSPI(baudrate = 10000000, 
            polarity = 0, phase = 0, bits = 8, firstbit = SoftSPI.MSB,
            sck = Pin(device_config['sck'], Pin.OUT, Pin.PULL_DOWN),
            mosi = Pin(device_config['mosi'], Pin.OUT, Pin.PULL_UP),
            miso = Pin(device_config['miso'], Pin.IN, Pin.PULL_UP))
else:
    logentry="Configuring ESP8266"
    logtime=time.localtime()
    log.write("{}.{}.{} {}:{}:{} - {}\n".format(logtime[2],logtime[1],logtime[0],logtime[3]+TZ,logtime[4],logtime[5],logentry))
    device_spi = SoftSPI(baudrate = 10000000, 
            polarity = 0, phase = 0, bits = 8, firstbit = SoftSPI.MSB,
            sck = Pin(device_config['sck'], Pin.OUT),
            mosi = Pin(device_config['mosi'], Pin.OUT, Pin.PULL_UP),
            miso = Pin(device_config['miso'], Pin.IN, Pin.PULL_UP))

wdt.feed()
    
lora = SX127x(device_spi, pins=device_config, parameters=lora_parameters)
wdt.feed()

# MQTT callback for messages on subscribed topics
def sub_cb(topic,msg):
## Uncomment for logging to file each MQTT-->LoRa message 
#    logentry=str(msg)
#    logtime=time.localtime()
#    log.write("{}.{}.{} {}:{}:{} - {}\n".format(logtime[2],logtime[1],logtime[0],logtime[3]+TZ,logtime[4],logtime[5],logentry))
    if str(topic).split('/')[1] in gw_config['no_lora']:
#         logentry="Root topic {} in blacklist.\n".format(str(topic).split('/')[0])
#         logtime=time.localtime()
#         log.write("{}.{}.{} {}:{}:{} - {}\n".format(logtime[2],logtime[1],logtime[0],logtime[3]+TZ,logtime[4],logtime[5],logentry))
        return
    send(lora,topic.decode(ENCODING),msg.decode(ENCODING))
#    logentry="Message sent to LoRa."
#    logtime=time.localtime()
#    log.write("{}.{}.{} {}:{}:{} - {}\n".format(logtime[2],logtime[1],logtime[0],logtime[3]+TZ,logtime[4],logtime[5],logentry))

# Configure MQTT
logentry="Configuring MQTT."
logtime=time.localtime()
log.write("{}.{}.{} {}:{}:{} - {}\n".format(logtime[2],logtime[1],logtime[0],logtime[3]+TZ,logtime[4],logtime[5],logentry))
c = MQTTClient(client_id=mqtt_config['mqtt_client'], 
               server=mqtt_config['mqtt_broker'], 
               user=mqtt_config['mqtt_user'], 
               password=mqtt_config['mqtt_pwd'],
               port=mqtt_config['mqtt_port'])
c.DEBUG=True
c.set_callback(sub_cb)
wdt.feed()
c.connect()
wdt.feed()
print(gw_config['gw_topic']+'/'+gw_config['gw_id'])
# LoRaMQTTGateway is subscribed to topic gw_topic/gw_id and its subtopics
c.subscribe(gw_config['gw_topic']+'/'+gw_config['gw_id'])
c.subscribe(gw_config['gw_topic']+'/'+gw_config['gw_id']+'/#')
print("MQTT broker {} connected!".format(mqtt_config['mqtt_broker']))
logentry="MQTT broker {} connected!".format(mqtt_config['mqtt_broker'])
logtime=time.localtime()
log.write("{}.{}.{} {}:{}:{} - {}\n".format(logtime[2],logtime[1],logtime[0],logtime[3]+TZ,logtime[4],logtime[5],logentry))

# Sending to LoRa
def send(lora,topic,message):
## Uncomment for logging to file each message sent to LoRa - default is to log only failed transmissions
#    logentry="Sending message to LoRa."
#    logtime=time.localtime()
#    log.write("{}.{}.{} {}:{}:{} - {}\n".format(logtime[2],logtime[1],logtime[0],logtime[3]+TZ,logtime[4],logtime[5],logentry))
    topic_elements=topic.split('/')
    topic_lora=topic_elements[1]
    if len(topic_elements)>2:
        for k in range(len(topic_elements)-2):
            topic_lora=topic_lora+"/"+topic_elements[k+2]
    payload = '{"topic":"'+topic_lora+'", "msg":"'+message+'"}'
    logtime=time.localtime()
    print("{}.{}.{} {}:{}:{} - MQTT>LoRa - {}".format(logtime[2],logtime[1],logtime[0],logtime[3]+TZ,logtime[4],logtime[5],payload))
    if module_config['has_oled']==1:
        oled.fill(0)
        oled.text("TX to LoRa:",0,0)	
        oled.text("{}".format(topic),0,10)
        pos=20
        x=12 
        res=[message[y-x:y] for y in range(x, len(message)+x,x)]
        for y in res:
            oled.text(y,0,pos)
            pos+=10
        oled.show()
    try:
        lora.println(payload)
    except:
        print("TX failed.")
        if module_config['has_oled']==1:
            oled.text("TX failed.",0,40)
            oled.show()
        logentry="Sending to LoRa failed."
        logtime=time.localtime()
        log.write("{}.{}.{} {}:{}:{} - {}\n".format(logtime[2],logtime[1],logtime[0],logtime[3]+TZ,logtime[4],logtime[5],logentry))

# Receiving from LoRa
def receive(lora):
    if lora.received_packet():
        lora.blink_led()
        payload = lora.read_payload()
        print("{}.{}.{} {}:{}:{} - LoRa>MQTT - RSSI: {} - {}".format(logtime[2],logtime[1],logtime[0],logtime[3]+TZ,logtime[4],logtime[5],lora.packet_rssi(),payload.decode(ENCODING)))
## Uncomment for logging to file each packet received from LoRa
#        logentry="Received LoRa packet: {}\n".format(payload)
#        logtime=time.localtime()
#        log.write("{}.{}.{} {}:{}:{} - {}\n".format(logtime[2],logtime[1],logtime[0],logtime[3]+TZ,logtime[4],logtime[5],logentry))
        if module_config['has_oled']==1:
            oled.fill(0)
            oled.text("RX from LoRa:",0,0)	
            oled.text("RSSI: {0}".format(lora.packet_rssi()),0,10)
            pos=20
            x=12 
            res=[payload[y-x:y] for y in range(x, len(payload)+x,x)]
            for y in res:
                oled.text(y,0,pos)
                pos+=10
            oled.show()
        parsed=ujson.loads(payload)
        if len(parsed['topic'].split('/'))>=2:
            if parsed['topic'].split('/')[0] in gw_config['no_mqtt']:
#                logentry="Root topic {} in blacklist.\n".format(parsed['topic'].split('/')[0])
#                logtime=time.localtime()
#                log.write("{}.{}.{} {}:{}:{} - {}\n".format(logtime[2],logtime[1],logtime[0],logtime[3]+TZ,logtime[4],logtime[5],logentry))
                return
            if len(gw_config['local'])>0 and parsed['topic'].split('/')[0] == gw_config['local']:
#                logentry="Root topic {} retransmitted locally.\n".format(parsed['topic'].split('/')[0])
#                logtime=time.localtime()
#                log.write("{}.{}.{} {}:{}:{} - {}\n".format(logtime[2],logtime[1],logtime[0],logtime[3]+TZ,logtime[4],logtime[5],logentry))
                print('Retransmitting locally.')
                send(lora,parsed['topic'],parsed['msg'])
                return
            parsed_topic=bytes(gw_config['gw_topic']+'/'+gw_config['gw_id']+'/'+parsed['topic'], ENCODING)
            parsed_msg=bytes(parsed['msg'], ENCODING)
            c.publish(parsed_topic, parsed_msg)

# Send beacon - default is to log only failed beacon transmissions
def send_beacon():
    global lora, oled, TZ
    beacontime=time.localtime()
    payload='{"time":"'+str(beacontime)+'", "gateway":"'+gw_config['gw_id']+'"}'
    print("LoRa Beacon: "+payload)
    if module_config['has_oled']==1:
        oled.fill(0)
        oled.text("LoRa Beacon:",0,0)	
        pos=10
        x=12 
        res=[payload[y-x:y] for y in range(x, len(payload)+x,x)]
        for y in res:
            oled.text(y,0,pos)
            pos+=10
        oled.show()
## Uncomment for logging to file each beacon
#    logentry="Sending beacon."
#    logtime=time.localtime()
#    log.write("{}.{}.{} {}:{}:{} - {}\n".format(logtime[2],logtime[1],logtime[0],logtime[3]+TZ,logtime[4],logtime[5],logentry))
    try:
        lora.println(payload)
#        logentry="Beacon sent."
#        logtime=time.localtime()
#        log.write("{}.{}.{} {}:{}:{} - {}\n".format(logtime[2],logtime[1],logtime[0],logtime[3]+TZ,logtime[4],logtime[5],logentry))
    except:
        print("Sending failed.")
        if module_config['has_oled']==1:
            oled.text("TX failed.",0,40)
            oled.show()
        logentry="Sending beacon failed."
        logtime=time.localtime()
        log.write("{}.{}.{} {}:{}:{} - {}\n".format(logtime[2],logtime[1],logtime[0],logtime[3]+TZ,logtime[4],logtime[5],logentry))

if gw_config['beacon_min']>0:
    last_beacon=int(time.time()/60)
    logentry="Beacon interval set to {}".format(gw_config['beacon_min'])
    logtime=time.localtime()
    log.write("{}.{}.{} {}:{}:{} - {}\n".format(logtime[2],logtime[1],logtime[0],logtime[3]+TZ,logtime[4],logtime[5],logentry))

# Main loop
while True:
    # Checking for LoRa packets
    try:
        receive(lora)
        wdt.feed()
    except:
        print("Receiving from LoRa failed.")
        logentry="Receiving from LoRa failed."
        logtime=time.localtime()
        log.write("{}.{}.{} {}:{}:{} - {}\n".format(logtime[2],logtime[1],logtime[0],logtime[3]+TZ,logtime[4],logtime[5],logentry))
        if module_config['has_oled']==1:
            oled.fill(0)
            oled.text("RX from LoRa failed.",0,0)
            oled.show()
        wdt.feed()
    # Checking for MQTT messages
    try:
        if nic.isconnected():
            c.check_msg()
            wdt.feed()
        else:
            logentry="WiFi disconnected. Reconnecting.."
            logtime=time.localtime()
            log.write("{}.{}.{} {}:{}:{} - {}\n".format(logtime[2],logtime[1],logtime[0],logtime[3]+TZ,logtime[4],logtime[5],logentry))
            nic.connect(wifi_config['ssid'], wifi_config['pwd'])
            while not nic.isconnected():
                wdt.feed()
                print("Waiting to connect ...")
                time.sleep(1)
            if len(wifi_config['ip_addr'])==0:
                ipaddr=nic.ifconfig()[0]
            else:
                nic.ifconfig((wifi_config['ip_addr'],wifi_config['ip_mask'],wifi_config['def_gw'],wifi_config['dns']))
                ipaddr=wifi_config['ip_addr']
            logentry="WiFi reconnected: {}".format(nic.ifconfig())
            logtime=time.localtime()
            log.write("{}.{}.{} {}:{}:{} - {}\n".format(logtime[2],logtime[1],logtime[0],logtime[3]+TZ,logtime[4],logtime[5],logentry))
            logentry="Reconnecting MQTT broker."
            logtime=time.localtime()
            log.write("{}.{}.{} {}:{}:{} - {}\n".format(logtime[2],logtime[1],logtime[0],logtime[3]+TZ,logtime[4],logtime[5],logentry))
            c.connect()
            wdt.feed()
            c.subscribe(gw_config['gw_topic']+'/'+gw_config['gw_id'])
            c.subscribe(gw_config['gw_topic']+'/'+gw_config['gw_id']+'/#')
            logentry="MQTT broker reconnected."
            logtime=time.localtime()
            log.write("{}.{}.{} {}:{}:{} - {}\n".format(logtime[2],logtime[1],logtime[0],logtime[3]+TZ,logtime[4],logtime[5],logentry))
            wdt.feed()
    except:
        print("Checking MQTT failed.")
        logentry="Checking MQTT failed."
        logtime=time.localtime()
        log.write("{}.{}.{} {}:{}:{} - {}\n".format(logtime[2],logtime[1],logtime[0],logtime[3]+TZ,logtime[4],logtime[5],logentry))
        if module_config['has_oled']==1:
            oled.fill(0)
            oled.text("Chk MQTT failed.",0,0)
            oled.show()
        wdt.feed()
    if gw_config['beacon_min']>0:
        current_time=int(time.time()/60)
        if current_time-last_beacon>=gw_config['beacon_min']:
            send_beacon()
            wdt.feed()
            last_beacon=current_time        
    wdt.feed()
