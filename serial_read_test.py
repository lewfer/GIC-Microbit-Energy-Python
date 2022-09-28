"""
test
"""

# Setup
###################################################################################################

# Set the port that the house microbit is connected to
# On windows go to device manager then ports
# On Mac and linux, from a terminal type ls /dev/ttyACM*
serialport = "COM5"

# Imports
###################################################################################################


import serial
#from random import randint
from time import sleep
import requests
from microbit import *


# Main
###################################################################################################


# Object to connect to microbit
microbit = Microbit(serialport)
microbit.connect()

# Run until the user asks to quit
running = True

# Main Pygame loop
while running:

    # Read values from Microbit
    reading = microbit.read()
    print(reading)


microbit.disconnect()

