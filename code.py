# Based on demo code at: https://learn.adafruit.com

# Needed for multiple reasons:
import board
import busio
import digitalio
# Needed for internet access: and fetching URLs
import ipaddress
import wifi
import ssl
import socketpool
import adafruit_requests
# Needed for date/time/string processing:
import time
from adafruit_datetime import datetime
# Needed for rotary encoder integration:
import rotaryio
# Needed for LCD panel integration:
import adafruit_character_lcd.character_lcd_spi as character_lcd
# Needed for Thermal Printer integration:
import adafruit_thermal_printer.thermal_printer_legacy
# Needed for NeoPixel and storage integration:
import neopixel

# URL to fetch:
TEXT_URL = "https://io.adafruit.com/api/v2/time/seconds"
# Number of seconds to delay start-up as CircuitPython seems to reload
# multiple times when saving files
DELAY_SEC = 2
# Number of printer lines to use as a buffer
LINE_FEED = 2
# Set to false to save paper when testing non-printing functions
USE_PAPER = True
# IP address to ping during configuration
ipv4 = ipaddress.ip_address("8.8.4.4")
# Initialize these for later use
button_state = None
last_position = None

print("-> Powered on! Hello World! Pausing to allow for reloads...")
time.sleep(DELAY_SEC)
print("-> Pause complete! Configuring...")

# Configure NeoPixel
pixel = neopixel.NeoPixel(board.NEOPIXEL, 1)
# Green for configuring
pixel.fill((0, 255, 0))

# Configure button switch as digital with pull-up resistor
# Button switch pin = "A1" aka "GPIO17" aka "D17"
button = digitalio.DigitalInOut(board.D17)
button.direction = digitalio.Direction.INPUT
button.pull = digitalio.Pull.UP

# Configure rotary encoder inputs
# Encoder pins = "A2"/"A3" aka "GPIO8"/"GPIO9" aka "D8"/"D9"
# Arrange "D8"/"D9" as needed below to set direction
encoder = rotaryio.IncrementalEncoder(board.D9, board.D8)

# Configure LCD character panel
spi = busio.SPI(board.SCK, MOSI=board.MOSI)
latch = digitalio.DigitalInOut(board.D37)
cols = 20
rows = 4
lcd = character_lcd.Character_LCD_SPI(spi, latch, cols, rows)

# Configure thermal printer
uart = busio.UART(board.TX, board.RX, baudrate=19200)
ThermalPrinter = adafruit_thermal_printer.get_printer_class(2.16)
printer = ThermalPrinter(uart)

def say(*tuple):
    "Function to simplify output"
    print("-> " + " ".join(tuple))
    lcd.message = " ".join(tuple)
    return

say("My MAC addr:" + str([hex(i) for i in wifi.radio.mac_address]) + "\nConfiguring...")

# Get wifi details and more from a secrets.py file
try:
    from secrets import secrets
except ImportError:
    say("WiFi secrets are kept in secrets.py, please add them there!")
    raise

# Try to get online
say("Attempting connection to %s"%secrets["ssid"])
try:
    wifi.radio.connect(secrets["ssid"], secrets["password"])
    say("Connected to %s!"%secrets["ssid"])
except:
    say("Unable to connect to %s!"%secrets["ssid"])
    say("Available WiFi networks:")
    for network in wifi.radio.start_scanning_networks():
        say("\t%s\t\tRSSI: %d\tChannel: %d" % (str(network.ssid, "utf-8"),
                network.rssi, network.channel))
    wifi.radio.stop_scanning_networks()
    raise

# Show online information and set up networking
say("My IP address is", str(wifi.radio.ipv4_address))
say("Ping google.com: %f ms" % (wifi.radio.ping(ipv4)*1000))

pool = socketpool.SocketPool(wifi.radio)
requests = adafruit_requests.Session(pool, ssl.create_default_context())

def fetch_time(str):
    "This function accepts a URL and returns an integer Unix timestamp"
    say("Fetching text from:", str)
    try:
        response = requests.get(str)
    except:
        say("Unable to fetch", str)
        raise
    output = int(response.text)
    return output

# Pull the time as a test, but don't say
unixtime = fetch_time(TEXT_URL)
out_string = datetime.fromtimestamp(unixtime).isoformat() + "Z"
say("Test timestamp:", out_string)

# Try to load a saved file and use it if found
try:
    with open("/count.txt", "r") as count_log:
        position_original = int(count_log.read())
        say("Loaded saved Count: " + str(position_original))
except:
    position_original = 0
    say("No saved count to load")

say("Configured! Awaiting rotary input to adjust Count; press button to print...")
# Light blue for awaiting input
pixel.fill((0, 0, 128))

# Input-gathering loop
while True:
    position_delta = int(encoder.position)
    position = position_original + position_delta
    if last_position is None or position != last_position:
        lcd.clear()
        say("Count: %d"%position)
    last_position = position
    if not button.value and button_state is None:
        button_state = "pressed"
    if button.value and button_state == "pressed":
        # Light red for input received
        pixel.fill((128, 0, 0))
        # Assume that if the button is pressed, we want at least one timestamp
        if position == 0: position = 1
        # Assume that a negative count should be positive
        position = abs(position)
        # Log the new position/count
        try:
            with open("/count.txt", "w") as count_log:
                    # Brighten the NeoPixel on every write...
                    pixel.fill((255, 0, 0))
                    count_log.write('{}\n'.format(position))
                    count_log.flush()
                    pixel.fill((128, 0, 0))  # Then return it to light red
        except OSError as e:  # When the filesystem is NOT writable by CircuitPython...
            delay = 0.5  # ...blink the NeoPixel every half second.
            if e.args[0] == 28:  # If the file system is full...
                delay = 0.15  # ...blink the NeoPixel every 0.15 seconds!
            while True:
                pixel.fill((255, 0, 0))
                time.sleep(delay)
                pixel.fill((0, 0, 0))
                time.sleep(delay)
        lcd.clear()
        say("Button pressed! Preparing to print %d timestamps..."%position)
        # Pull the time once, then count up from there
        unixtime = fetch_time(TEXT_URL)
        # Iterate up from zero so we can track our position
        for i in range(0, position):
            # Build the time from our iteration plus our fetched time
            loop_time = unixtime + i
            # Generate our ISO-8601 time stamp
            out_datetime = datetime.fromtimestamp(loop_time).isoformat() + "Z"
            # Split the ISO-8601 time stamp into date and time
            out_split = out_datetime.split("T")
            # The date is just the first item in the list we just made
            out_date = out_split[0]
            # The time is the second item in the list, plus the T we lost above
            out_time = "T" + out_split[1]
            # Build the final string, which doesn't need loop_time because
            # it's included in the barcode output
            out_string = out_date + "\n" + out_time
            display_string = "Printing: " + str(i + 1) + " of " + str(position) + "\n" + str(loop_time) + "\n" + out_string
            lcd.clear()
            say(display_string)
            if (USE_PAPER == True):
                # Center justify
                printer.justify = adafruit_thermal_printer.JUSTIFY_CENTER
                # Print the barcode
                printer.print_barcode(str(loop_time), printer.CODE128)
                # Large size
                printer.size = adafruit_thermal_printer.SIZE_LARGE
                # Print the output
                printer.print(out_string)
                # Give a little room at the bottom
                printer.feed(LINE_FEED)
            # Wait one second so we can't overlap previous runs
            time.sleep(1)
        button_state = None
        say("Printing complete! Awaiting rotary input to adjust Count; press button to print...")
        # Light blue for awaiting input
        pixel.fill((0, 0, 128))
        # Re-draw the final screen to leave a clean display
        lcd.clear()
        say("Count: %d"%position)
