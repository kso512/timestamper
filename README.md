# timestamper

*timestamper:* A Time Stamp Printer

## Introduction

The goal of this project is quickly and easily generating a series of unique slips of paper, for use in labeling and other forms of keeping things in order.

## User Stories

The primary "user story" is: the user comes home from the grocery store with lots of items, and would like to affix unique timestamps on each while putting them away.  After counting the number of items, the device can be powered on and set to generate that number of items. It will then print that many unique timestamp slips.  Scissors and tape can be used to separate them from each other, and adhere them to the groceries, respectively.  This allows older items to be easily identified, especially if care is taken to place "younger" timestamp slips on "younger" groceries per available "created on" or "best by" dates.

Secondarily, one-offs can be created and added to more significant projects, such as mounting something to a wall, putting together furniture, or marking a special time.

Generally, if a unique yet anonymous hard-copy identifier is needed, and a rate of one-per-second is fast enough, this might work for you!

## Operation

Outputs are a LCD panel (20 columns by 4 rows) to display text, a NeoPixel to indicate status by color, and a "count.txt" file on the CircuitPython drive to retain that number between boots.  The NeoPixel will show green for configuring, blue for awaiting input, and red for taking action based on a button press or file write.

Input is received from the user via the rotary encoder and the integrated switch.  By turning the rotary encoder and watching the "Count" presented on the LCD panel, the user can tell the timestamper how many slips to print.  Once a proper count is selected, the user can then depress the integrated switch and the timestamper will retrieve the current time and begin printing.

## Hardware Setup

### Required Hardware

* [Adafruit QT Py ESP32-S2 WiFi Dev Board with uFL Antenna Port - STEMMA QT](https://www.adafruit.com/product/5348)
  * Central processing of inputs/outputs
  * Update date/time via wifi
* [2.4GHz Mini Flexible WiFi Antenna with uFL Connector - 100mm](https://www.adafruit.com/product/2308)
  * This antenna (or something similar) is needed for the QT Py to achieve a decent wifi signal
* [20x4 LCD display](https://www.adafruit.com/product/198)
  * Used to indicate how many timestamps to print, status, etc.
* [i2c/SPI LCD Backpack](https://www.adafruit.com/product/292)
  * Connects LCD display to QT Py over SPI bus
* [Rotary Encoder in CircuitPython](https://www.adafruit.com/product/377)
  * Rotate to set number of iterations (timestamps to generate)
  * Press to execute
* [Mini Thermal Receipt Printer Starter Pack](https://www.adafruit.com/product/600)
  * Prints timestamps from QT Py over serial bus, via voltage divider
  * Starter pack includes critical components such as a power supply and connectors
* Resistors for voltage divider (5VDC -> 3.3VDC), one each
  * 2.2k
  * 3.3k

### Building

See the included Fritzing file (`timestamper.fzz`) for "breadboard" and "schematic" views, which show all the required connections.  Use a breadboard at first, then transfer and solder onto something more permanent like a Perma-Proto once everything is working.

To act as an enclosure, I used a plastic tub and lid.  The lid acts as a "panel" to mount the printer and user interface to, and the tub contains the wires and spare paper rolls.

#### Prototype Unit

From left to right: thermal printer, breadboard, LCD Panel with backpack; on the breadboard, from left to right: rotary encoder, voltage divider, QT Py with antenna

![Picture of prototype unit](/prototype.png "Picture of prototype unit")

#### Assembled Unit

Internal view from left to right: thermal printer, perma-proto board, LCD Panel with backpack; on the perma-proto board, from top to bottom: voltage divider, LCD panel connector, rotary encoder (on reverse side), QT Py with antenna

![Picture of assembled unit, back](/assembled-back.png "Picture of assembled unit, back")

External view from left to right: thermal printer, rotary encoder, LCD panel

![Picture of assembled unit, front](/assembled-front.png "Picture of assembled unit, front")

### Consumables

* Thermal receipt printer paper
* Clear packing tape

**NOTE**: Test your combination of paper and tape for fading by printing some test slips and applying tape directly to the "inked" surface.  If fading occurs within a week, try another tape/paper combination, or use a small inverted (sticky-to-sticky) piece of tape to protect the "inked" surface from the adhesive that would touch it.

## Software Setup

* [Flash the QT Py with CircuitPython](https://learn.adafruit.com/adafruit-qt-py-esp32-s2/circuitpython), so a new drive named `CIRCUITPY` is created.
* Create on the `CIRCUITPY` drive:
  * A `secrets.py` file with [WiFi SSID and credentials](https://learn.adafruit.com/adafruit-qt-py-esp32-s2/circuitpython-internet-test#secrets-file-3077419-5)
* Copy to the `CIRCUITPY` drive:
  * The required libraries from the [Adafruit CircuitPython Library Bundle](https://docs.circuitpython.org/projects/bundle/en/latest/), under the `/lib` folder:
    * [adafruit_74hc595](https://docs.circuitpython.org/projects/74hc595/en/latest/)
    * [adafruit_character_lcd](https://docs.circuitpython.org/projects/character_lcd/en/latest/)
    * [adafruit_datetime](https://docs.circuitpython.org/projects/datetime/en/latest/)
    * [adafruit_requests](https://docs.circuitpython.org/projects/requests/en/latest/)
    * [adafruit_thermal_printer](https://docs.circuitpython.org/projects/thermal_printer/en/latest/)
  * `boot.py`
  * `code.py`

Example secrets.py:

    $ cat /media/user/CIRCUITPY/secrets.py
    secrets = {
        'ssid' : 'ChangeToYourWifiSSID',
        'password' : 'ChangeToYourWifiPassword',
        }

Required files and folder structure:

    $ tree /media/user/CIRCUITPY/
    /media/user/CIRCUITPY/
    ├── boot.py
    ├── code.py
    ├── lib
    │   ├── adafruit_74hc595.py
    │   ├── adafruit_character_lcd
    │   │   ├── character_lcd_i2c.py
    │   │   ├── character_lcd.py
    │   │   ├── character_lcd_rgb_i2c.py
    │   │   ├── character_lcd_spi.py
    │   │   └── __init__.py
    │   ├── adafruit_datetime.py
    │   ├── adafruit_requests.py
    │   ├── adafruit_thermal_printer
    │   │   ├── __init__.py
    │   │   ├── thermal_printer_2168.py
    │   │   ├── thermal_printer_264.py
    │   │   ├── thermal_printer_legacy.py
    │   │   └── thermal_printer.py
    │   └── neopixel.py
    └── secrets.py
    
    3 directories, 17 files

## Design Goals & Decisions

* Efficient code - only call out to the Internet as needed, not each loop
* Freshness over independence - doesn't rely on internal counters
* Long-term - works as well the 100th time as the 1st time
* Low-power - uses less power than the existing Raspberry Pi solution, aims to minimize power consumption in the future
* Portable - only needs a power cable; gets online without a network cable
* Ratcheting - avoids creating two records twice, always incrementing and avoiding overruns of previous work
* Robust - tests for failures and handles them gracefully; does not assume everything goes perfect every time
* Simple to use - one knob to turn, one button to press
* User-friendly - build a high barrier between the user and failure scenarios, such as continuing after a failure, telling the user they are wrong for trying to use zero or a negative number when allowed by the interface, etc.

## TODO / Future Improvements

### Automation

* Include QR-codes for encoding more data than a barcode
* Integrations with webhooks/APIs to update online databases/inventories

### Power conservation

* Relay, transistor, etc. to control power to the thermal printer
* Standby mode to reduce overall power consumption

### Storage

* Total timestamps generated
* Log of each timestamp generated

### User Interface

* Fine-tune code to closer meet Design Goals & Decisions
* Add screenshots and pictures
* Use the Neo-Pixel to indicate status or activity, beyond what's shown on the LCD panel
* Maybe go ahead and add a RTC, or go full-blown GPS

## Pitfalls and Lessons Learned

While initially it appeared useful, the [adafruit_ntp](https://docs.circuitpython.org/projects/ntp/en/latest/api.html) library appears to require a very specific ESP32 SPI integration that the ESP32-S2 unit available does not possess.  That is why the "long way" is used to pull a URL, then extract a useable time from that.  Copying/pasting the sample code results in this error:

    Traceback (most recent call last):
    File "code.py", line 9, in <module>
    AttributeError: 'module' object has no attribute 'ESP_CS'

Printing as fast as possible without reliable tracking of previous runs can allow for duplicate timestamps to be created, which goes against the whole idea of unique slips of paper.  Early prototype example generated by repeatedly pressing the button and the `time.sleep(1)` line commented out:

    -> Button pressed! Printing 1 timestamps...
    -> Timestamp:
    1652661770
    2022-05-16T00:42:50Z
    -> Printing complete! Awaiting rotary input to set Position; press button to print...
    -> Button pressed! Printing 1 timestamps...
    -> Timestamp:
    1652661770
    2022-05-16T00:42:50Z
    -> Printing complete! Awaiting rotary input to set Position; press button to print...

## References

* [Adafruit IO Time Service](https://io.adafruit.com/api/docs/#time)
* [Adafruit Learning System](https://learn.adafruit.com/)
  * [i2c/SPI LCD Backpack](https://learn.adafruit.com/i2c-spi-lcd-backpack)
  * [Rotary Encoder in CircuitPython](https://learn.adafruit.com/rotary-encoder)
  * [Adafruit QT Py ESP32-S2 WiFi Dev Board with uFL Antenna Port - STEMMA QT](https://learn.adafruit.com/adafruit-qt-py-esp32-s2)
  * [Mini Thermal Receipt Printer](https://learn.adafruit.com/mini-thermal-receipt-printer)
* [CircuitPython Reference Documentation](https://docs.circuitpython.org/en/latest/README.html)
  * [adafruit_74hc595](https://docs.circuitpython.org/projects/74hc595/en/latest/)
  * [adafruit_character_lcd](https://docs.circuitpython.org/projects/character_lcd/en/latest/)
  * [adafruit_datetime](https://docs.circuitpython.org/projects/datetime/en/latest/)
  * [adafruit_requests](https://docs.circuitpython.org/projects/requests/en/latest/)
  * [adafruit_thermal_printer](https://docs.circuitpython.org/projects/thermal_printer/en/latest/)
* [W3Schools](https://www.w3schools.com/)
  * [Python Functions](https://www.w3schools.com/python/python_functions.asp)
  * [Python Math](https://www.w3schools.com/python/python_math.asp)
  * [Python String join() Method](https://www.w3schools.com/python/ref_string_join.asp)
  * [Python String split() Method](https://www.w3schools.com/python/ref_string_split.asp)
  * [Python String splitlines() Method](https://www.w3schools.com/python/ref_string_splitlines.asp)
  * [Python try Keyword](https://www.w3schools.com/python/ref_keyword_try.asp)
