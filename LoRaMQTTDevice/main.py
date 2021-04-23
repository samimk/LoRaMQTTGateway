import time
from config import *
from machine import Pin, SoftSPI, SoftI2C, Timer, WDT
from sx127x import SX127x
if module_config['has_oled']==1:
    from ssd1306 import SSD1306_I2C
import machine

# Device version
DEV_VER=0.1

# Encoding used
ENCODING='latin2'

counter=0

# Watchdog timer initialization
wdt = WDT()
print("Watchdog timer initialized.")

# For boards with OLED based on SSD1306
if module_config['has_oled']==1:
    print("Configuring OLED.")
    
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
    oled.text('LoRaMQTTDev '+str(DEV_VER), 0, 20)
    oled.show()
    print("OLED configured")

if module_config['module_type']=='ESP32':
    print("Configuring ESP32.")
    device_spi = SoftSPI(baudrate = 10000000, 
            polarity = 0, phase = 0, bits = 8, firstbit = SoftSPI.MSB,
            sck = Pin(device_config['sck'], Pin.OUT, Pin.PULL_DOWN),
            mosi = Pin(device_config['mosi'], Pin.OUT, Pin.PULL_UP),
            miso = Pin(device_config['miso'], Pin.IN, Pin.PULL_UP))
else:
    print("Configuring ESP8266")
    device_spi = SoftSPI(baudrate = 10000000, 
            polarity = 0, phase = 0, bits = 8, firstbit = SoftSPI.MSB,
            sck = Pin(device_config['sck'], Pin.OUT),
            mosi = Pin(device_config['mosi'], Pin.OUT, Pin.PULL_UP),
            miso = Pin(device_config['miso'], Pin.IN, Pin.PULL_UP))

wdt.feed()
    
lora = SX127x(device_spi, pins=device_config, parameters=lora_parameters)

wdt.feed()

# Sending to LoRa
def send(lora,topic,message):
    payload = '{"topic":"'+topic+'", "msg":"'+message+'"}'
    print("To LoRa -->  {}".format(payload))
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
        print("Sending to LoRa failed.")

# Receiving from LoRa
def receive(lora):
    
    if lora.received_packet():
        lora.blink_led()
        payload = lora.read_payload()
        print("Fm LoRa --> RSSI: {} - {}".format(lora.packet_rssi(),payload.decode(ENCODING)))
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
        return payload.decode(ENCODING)
    else:
        return ""

last_xmit=time.time()

# Preparing data to be sent
# This function should collect data from sensor(s) and prepare message as string
def get_data():
    global counter
    counter+=1
    msg=dev_config['dev_id']+': '+str(counter)
    return msg

# Main loop
while True:
    # Checking for LoRa packets
    try:
        received_msg=receive(lora)
    except:
        print("Receiving from LoRa failed.")
        if module_config['has_oled']==1:
            oled.fill(0)
            oled.text("RX from LoRa failed.",0,0)
            oled.show()

    wdt.feed()

    # Sending LoRa message
    current_time=time.time()
    if current_time-last_xmit>=dev_config['xmit_period']:
        msg=get_data()
        topic=dev_config['dev_topic']+'/'+dev_config['dev_id']
        send(lora,topic,msg)
        wdt.feed()
        last_xmit=current_time        

    wdt.feed()
