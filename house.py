"""
house.py

Interfaces between Microbit controlling the house and the web service (national grid).
Also provides a UI to show what's happening in the house.

Reads available energy from the national grid and turns on whatever devices can be powered.
"""

# Setup
###################################################################################################


# Define the devices we need to power
devices = {"light":     {"power":100, "on":1, "powered":0}, 
           "toaster":   {"power":100, "on":1, "powered":0}, 
           "car":       {"power":100, "on":1, "powered":0}, 
           "tv":        {"power":100, "on":1, "powered":0}, 
           "dishwasher":{"power":100, "on":1, "powered":0}}


# Imports
###################################################################################################

import pygame
from pygame.locals import *
import serial
from time import sleep
import random
import requests
from microbit import *
from utils import *
from settings import *

# Main
###################################################################################################

# Object to connect to microbit
microbit = Microbit(house_serialport)
microbit.connect()

# Startup pygame window
pygame.init()
screen = pygame.display.set_mode([500, 500])

# Run until the user asks to quit
running = True

# Work out total energy needed
totalEnergyNeeded = 0
for i, key in enumerate(devices):
    if devices[key]["on"]:
        devicePowerNeeded = devices[key]["power"]
        totalEnergyNeeded += devicePowerNeeded
print("totalEnergyNeeded",totalEnergyNeeded)

# Main Pygame loop
while running:

    # Did the user click the window close button?
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Fill the background with white
    screen.fill((255, 255, 255))            

    # Find out how much energy is available
    url = "http://lewfer.pythonanywhere.com/gettotalenergy"
    response = requests.get(url)
    totalEnergy = int(response.json())
    print(totalEnergy)

    # Draw bar to show avail energy vs needed energy
    bar = map(min(totalEnergyNeeded*2,totalEnergy), 0, totalEnergyNeeded*2, 0, 480)
    color = red if totalEnergy<totalEnergyNeeded else yellow if totalEnergy<totalEnergyNeeded*1.5 else green
    pygame.draw.rect(screen, color, (10,10,bar,50))    
    pygame.draw.rect(screen, black, (10,10,240,50), 2)
    textLeft(screen, 10, 10, str(totalEnergy))

    # Power each device until we run out of energy
    totalEnergyUsed = 0
    for i, key in enumerate(devices):
        if devices[key]["on"]:
            devicePowerNeeded = devices[key]["power"]
            if devicePowerNeeded <= totalEnergy:
                devices[key]["powered"] = 1
                totalEnergyUsed += devicePowerNeeded
                totalEnergy -= devicePowerNeeded
            else:
                devices[key]["powered"] = 0
    print(f"Total energy used {totalEnergyUsed}")

    # Tell National Grid how much we used
    url = f"http://lewfer.pythonanywhere.com/use?energy={totalEnergyUsed}"
    response = requests.get(url)
    print(response.json())

    # Tell microbit which devices to turn on
    for i, key in enumerate(devices):
        if devices[key]["on"] and devices[key]["powered"]:
            message = f"{key}=1\n"
        else:
            message = f"{key}=0\n"
        microbit.write(message)
        print("Sending:",message)

    print(devices)

    #print("write")
    #totalEnergy = random.randrange(0,200)
    #print(totalEnergy)
    #microbit.write(f"{totalEnergy}\n")



    # Draw devices
    for i, key in enumerate(devices):
        color = green if devices[key]["on"] and devices[key]["powered"] else grey
        pygame.draw.rect(screen, color, (10,100+32*i,480,30))
        textLeft(screen, 10, 100+32*i,key)

    sleep(1)

    # Update the display (flip the in-memory buffer on to the screen)
    pygame.display.flip()

microbit.disconnect()

# Done! Time to quit.
pygame.quit()