# Copyright 2020 LeMaRiva|tech lemariva.com
# Modifications copyright (C) 2021 Samim Konjicija
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

# WiFi config
wifi_config = {
    'ssid' : 'ENTER_WLAN_SSID',
    'pwd' : 'ENTER_WLAN_PASSWORD',
    'ip_addr' : '192.168.0.10',    # Empty string for DHCP
    'ip_mask' : '255.255.255.0',   # Empty string for DHCP
    'def_gw' : '192.168.0.1',      # Empty string for DHCP
    'dns' : '8.8.8.8'              # Empty string for DHCP
}

mqtt_config = {
    'mqtt_broker' : 'ENTER_MQTT_BROKER_URL',
    'mqtt_port' : 1883,
    'mqtt_user' : 'ENTER_MQTT_BROKER_USER',
    'mqtt_pwd' : 'ENTER_MQTT_BROKER_PASSWORD',
    'mqtt_client' : 'LORA_GATEWAY_1'
}

# Gateway config
gw_config = {
    'gw_topic':'lora',  # Enter root topic for lora MQTT messages
    'gw_id':'gateway1', # Enter LoRa Gateway ID as string
    'beacon_min': 1  # 0 - no beacon, >0 - beacon interval (in minutes)
}

# Module config
module_config = {
    'has_oled': 1,   # 1 - module has OLED display, 0 - module without display
    'module_type':'ESP32'  # Module used - ESP8266 or ESP32
}

# LoRa parameters config
lora_parameters = {
    'frequency': 433.175E6, 
    'tx_power_level': 17, # max. 14 without PA, 17 with PA
    'signal_bandwidth': 125E3,    
    'spreading_factor': 8,  # 7-12
    'coding_rate': 5, 
    'preamble_length': 8,
    'implicit_header': False, 
    'sync_word': 0x12, 
    'enable_CRC': False,
    'invert_IQ': False,
}

# LoRa device config for various board models - edit if necessary

"""
# ESP8266 
device_config = {
    'miso':12,
    'mosi':13,
    'ss':15,
    'sck':14,
    'dio_0':5,
    'reset':4,
    'led':2, 
}

"""

# ES32 TTGO v1.0 
device_config = {
    'miso':19,
    'mosi':27,
    'ss':18,
    'sck':5,
    'dio_0':26,
    'reset':14,
    'led':2, 
}

"""
# M5Stack ATOM Matrix
device_config = {
    'miso':23,
    'mosi':19,
    'ss':22,
    'sck':33,
    'dio_0':25,
    'reset':21,
    'led':12, 
}

# M5Stack & LoRA868 Module
device_config = {
    'miso':19,
    'mosi':23,
    'ss':5,
    'sck':18,
    'dio_0':26,
    'reset':36,
    'led':12, 
}
"""

app_config = {
    'loop': 200,
    'sleep': 100,
}
