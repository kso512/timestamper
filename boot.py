import time
import board
import digitalio
import storage
import neopixel

pixel = neopixel.NeoPixel(board.NEOPIXEL, 1)

button = digitalio.DigitalInOut(board.BUTTON)
button.switch_to_input(pull=digitalio.Pull.UP)

# Turn the NeoPixel blue for one second to indicate when to press the boot button.
pixel.fill((255, 255, 255))
time.sleep(1)

# If the button is connected to ground, the filesystem is writable by host
# This is the OPPOSITE of the original code, hence the "not()" added
storage.remount("/", readonly=not(button.value))
print("-> BOOT COMPLETE")
