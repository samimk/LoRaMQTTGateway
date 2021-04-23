# LoRaMQTTDevice
## Demo device for LoRaMQTTGateway
### Description
This application implements a demo LoRa device, which periodically sends a message to LoRaMQTTGateway.It is written for MicroPython running on ESP8266 or ESP32 boards. It uses Mauro Riva's module *sx127x.py* from his **uPyLoRaWAN** repository (https://github.com/lemariva/uPyLoRaWAN). The application has been tested on NodeMCU module (ESP8266), and Heltec's WiFi LoRa 32 module with OLED display (ESP32). For OLED display, old Adafruit's module *ssd1306.py* has been used (https://github.com/adafruit/micropython-adafruit-ssd1306).

### Configuration

All the necessary parameters can be configured in the file *config.py*:
- *dev_topic*, *dev_id* and *xmit_period*
- module type and presence of OLED display can be configured in *module_config*,
- parameters for LoRa can be configured in *lora_config*,
- SPI connection to SX127x module can be configured in *device_config*.

The LoRaMQTTDevice sends a string message to a topic *dev_topic/dev_period*.

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
