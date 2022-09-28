"""
test
"""

from settings import *

# Setup
###################################################################################################




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
microbit = Microbit(powerstation_serialport)
microbit.connect()

# Run until the user asks to quit
running = True

# Main Pygame loop
while running:

    # Read values from Microbit
    reading = microbit.read()
    print(reading)


microbit.disconnect()

