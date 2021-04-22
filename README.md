# LoRaMQTTGateway
## Basic gateway between LoRa devices and MQTT broker
### Description
This application provides basic gateway functionality between LoRa devices and MQTT broker. **LoRaMQTTGateway** is written for MicroPython running on ESP8266 or ESP32 boards. It uses Mauro Riva's module *sx127x.py* from his **uPyLoRaWAN** repository (https://github.com/lemariva/uPyLoRaWAN). The application has been tested on NodeMCU module (ESP8266), and Heltec's WiFi LoRa 32 module with OLED display (ESP32). For OLED display, old Adafruit's module *ssd1306.py* has been used (https://github.com/adafruit/micropython-adafruit-ssd1306).

### Motivation
LoRaWAN is surely a large-scale solution for integrating wireless devices into an IoT application. That made LoRaWAN infractructure too large and too complex for smaller applications, with relatively small number of wireless devices (less than a hundred). **LoRaMQTTGateway** is intended for such applications (such as smart home or similar). Since it exposes a widely-used MQTT to wireless devices, its integration into other existing systems should be very easy. 

Currently, no data encryption is used, having in mind that in most such cases data traffic is closed in a local network. Nevertheless, data encryption is one of the first features to be added to the LoRaMQTTGateway.

### LoRa messages and MQTT messages

**LoRaMQTTGateway** connects to a MQTT broker and subcribes topic defined as *gw_topic/gw_id* from fields in a file *config.py*, and all its subtopics. 

LoRa device sends a message as JSON string:
<pre><code>
  {
      "topic" : "topic_defined_by_device",
      "message" : "string_containing_message_from_device"
  }
</pre></code>

The *topic_defined_by_device* can also be hierarchical.

**LoRaMQTTGateway** appends the received topic to the predefined *gw_topic/gw_id* and forwards the received message as plain string. Since the gateway subscribes to *gw_topic/gw_id/#*, the forwarded message will be bounced back to LoRa as JSON string, but this time with topic *gw_id/topic_defined_by_device*. This serves for two purposes:
- eventually implementing retransmission from device, in case that the message hasn't been received,
- enabling the device to determine which gateway(s) forwarded message.

Message received from MQTT broker is transmitted to LoRa as JSON string:
<pre><code>
  {
      "topic" : "topic_for_LoRa",
      "message" : "string_containing_message_from_MQTT_broker"
  }
</pre></code>

The *topic_for_LoRa* is formed as the topic of the message received from MQTT broker, without the root *gw_topic*. The *string_containing_message_from_MQTT_broker* can also be formatted using JSON.

Additionally, the application can be configured to send a beacon to LoRa periodically. The beacon message contains timestamp and *gw_id*.

### Configuration

All the necessary parameters can be configured in the file *config.py*:
- WiFi connection can be configured in *wifi_config* (DHCP or static IP address can be used),
- MQTT broker connection can be configured in *mqtt_config*,
- *gw_topic*, *gw_id* and beacon interval can be configured in *gw_config*,
- module type and presence of OLED display can be configured in *module_config*,
- parameters for LoRa can be configured in *lora_config*,
- SPI connection to SX127x module can be configured in *device_config*.

All parameters are self-explanatory, and some are additionaly commented in the file *config.py*.

Files which need to be uploaded to the module are:
- *config.py*,
- *main.py*,
- *sx127x.py*,
- *ssd1306.py* (in case that OLED display is used).

### Use of the application on ESP8266-based modules

Some limitations exist when ESP8266-based module is used for gateway, due to memory constraints:
- file *sx127x.py* has to be pre-compiled to *sx127x.mpy*,
- file *main.py* has to be pre-compiled to *main.mpy*,
- file *boot.py* should be uploaded to the module (with only one line, to start main application).
