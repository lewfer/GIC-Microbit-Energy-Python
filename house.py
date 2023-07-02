"""
house.py

Interfaces between Microbit controlling the house and the web service (national grid).
Also provides a UI to show what's happening in the house.

Reads available energy from the national grid and turns on whatever devices can be powered.
"""

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
from threading import Thread

# Setup
###################################################################################################

# Run until the user asks to quit
running = True

# Set to true when microbit is ready
ready = False


# Pygame window parameters
windowWidth = 500
windowHeight = 600
maxBar = windowWidth-20
mousex = 0
mousey = 0
barheight = 30
bargap = 2

# Pygame colors
DEVICE_ON = (31,219,43)
DEVICE_OFF = grey
DEVICE_NOPOWER = (173,219,188)
#GAUGE_GOOD = (150,219,140)
#GAUGE_DANGER = (242,214,143)
#GAUGE_BAD = (235,120,123)
GAUGE_GOOD = (178,219,192)
GAUGE_DANGER = (245,237,201)
GAUGE_BAD = (237,200,198)
GAUGE_NODEMAND = grey
GAUGE_AVAILABLE = (235,71,0)
GAUGE_NEEDED = (166,40,235)
GAUGE_USED  = (50,49,245)

# Object to connect to microbit via serial
microbit = Microbit(house_serialport)
microbit.connect()

# Define the devices we need to power
# These will be populated by the microbit
devices = {}

# Data logging
dataNeeded = []
dataUsed = []

# Parameters to adjust
refreshPeriod = 1000    # how often to consume energy (milliseconds).  determines screen refresh rate
consumptionRate = 1/5   # proportion of device power used on each refresh period


# Functions
###################################################################################################

# Function to listen for serial messages from the microbit
# This will run on a separate thread to the pygame loop
def listen():
    global ready

    while running:
        try:
            message = microbit.read()
            #print("new message",message)

            if message=="clear":
                # Clear all devices
                ready = False
                devices.clear()
                #sleep(5)

            elif message=="ready":
                ready = True

            elif message.startswith("debug"):
                # Debug message from microbit
                print(message)

            elif message.startswith("get"):
                # Get on/off status for device
                split = message.split("=")
                device = devices[split[1]]
                if device["on"] and device["powered"]:
                    status = device["name"] + "=1\n"
                else:
                    status = device["name"] + "=0\n"
                #print(split[1], device,status)
                microbit.write(status)
                #print("Sending:",status)   

            elif (len(message)>0):
                # Adding a new device
                print("Receive:",message)
                split = message.split("=")
                devices[split[0]] = {"name":split[0], "power_needed":int(split[1]), "on":0, "powered":0}
        except Exception as e:
            print(e)
            pass

def getTotalEnergy():
    # Find out how much energy is available at the national grid
    url = grid_url + "/getavailableenergy"
    available = 0
    try:
        response = requests.get(url, timeout=5)
        available = int(response.json())
    except requests.exceptions.Timeout:
        pass

    return available

def useEnergy(units):
    # Tell National Grid how much we used
    print("Energy used:", totalEnergyUsed)
    url = grid_url + f"/use?energy={units}"
    response = requests.get(url)
    #print(response.json())

def getEnergyConsumption(totalEnergyAvailable):
    # Power each device (turn on "powered") until we run out of energy
    maxEnergyNeeded = 0     
    totalEnergyNeeded = 0  
    totalEnergyUsed = 0     
    for device in devices.values():
        devicePowerNeeded = device["power_needed"]
        maxEnergyNeeded += devicePowerNeeded
        if device["on"]:
            totalEnergyNeeded += devicePowerNeeded #*consumptionRate
            if devicePowerNeeded <= totalEnergyAvailable:
                device["powered"] = 1
                totalEnergyUsed += devicePowerNeeded #*consumptionRate
                totalEnergyAvailable -= devicePowerNeeded #*consumptionRate
            else:
                device["powered"] = 0    
    return maxEnergyNeeded,totalEnergyNeeded,totalEnergyUsed


# Main
###################################################################################################

# Create a new thread to listen from messages from the microbit
Thread(target=listen).start()


# Startup pygame window
pygame.init()
screen = pygame.display.set_mode([windowWidth, windowHeight])
pygame.display.set_caption('House Monitor')
icon = pygame.image.load('house.png')
pygame.display.set_icon(icon)

# Create objects on the screen
indicatorsTop = 140 # y position where indicators start
maxIndicators = 5
graph = Graph(100,indicatorsTop+(barheight+bargap)*maxIndicators+50,300,200, screen)

# Set a timer for how often to consume energy
CONSUMEENERGY= pygame.USEREVENT + 1 
pygame.time.set_timer(CONSUMEENERGY, refreshPeriod)

# Energy usage variables
maxEnergyNeeded = 0             # if all devices on
totalEnergyNeeded = 0           # for currently on devices
totalEnergyAvailable = 0        # what the powerstation can give
totalEnergyUsed = 0             # what was actually used


# Main Pygame loop
while running:

    # Check pygame events
    mousex = -1
    mousey = -1
    consumeEnergy = False 
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.MOUSEBUTTONDOWN:
            pos = pygame.mouse.get_pos()
            mousex, mousey = pos
        if event.type == CONSUMEENERGY:
            consumeEnergy = True

    # Fill the background with white
    screen.fill((255, 255, 255))       

    if ready:
        if consumeEnergy:

            # Find out how much energy is available at the national grid
            totalEnergyAvailable = getTotalEnergy()

            # Power each device (turn on "powered") until we reach the availability limit
            maxEnergyNeeded,totalEnergyNeeded,totalEnergyUsed = getEnergyConsumption(totalEnergyAvailable)

            # Tell National Grid how much we used
            if totalEnergyUsed>0:
                useEnergy(int(totalEnergyUsed))
            
            # Log the data
            dataNeeded.append(totalEnergyNeeded) #/consumptionRate)
            dataNeeded = dataNeeded[-144:]    
            dataUsed.append(totalEnergyUsed) #/consumptionRate)
            dataUsed = dataUsed[-144:]                


        # Draw bar to show avail energy vs needed energy
        # maxBar represents 2xmaxEnergyNeeded, so 1/2 maxbar, represented by the black box, is the maxEnergyNeeded
        bar = maxBar if totalEnergyNeeded==0 else map(min(maxEnergyNeeded*2,totalEnergyAvailable), 0, maxEnergyNeeded*2, 0, maxBar)
        neededBar = 0 if totalEnergyNeeded==0 else map(totalEnergyNeeded, 0, maxEnergyNeeded, 0, maxBar/2)
        color = red if totalEnergyAvailable<totalEnergyNeeded else yellow if totalEnergyAvailable<totalEnergyNeeded*1.5 else green
        pygame.draw.rect(screen, GAUGE_BAD, (10,10,maxBar/2,50))    
        pygame.draw.rect(screen, GAUGE_DANGER, (10+maxBar/2,10,maxBar/4,50))    
        pygame.draw.rect(screen, GAUGE_GOOD, (10+maxBar*3/4,10,maxBar/4,50))    
        pygame.draw.rect(screen, GAUGE_AVAILABLE , (10,20,bar,30))   
        if totalEnergyNeeded==0:
            pygame.draw.rect(screen, GAUGE_NODEMAND, (10,20,bar,30))  
        pygame.draw.rect(screen, GAUGE_NEEDED, (10,20,neededBar,30), 2)
        textLeft(screen, 10, 65, "Needed: "+str(totalEnergyNeeded), 16, GAUGE_NEEDED)
        textLeft(screen, 10, 85, "Available: "+str(totalEnergyAvailable), 16, GAUGE_AVAILABLE)
        textLeft(screen, 10, 105, "Used: "+str(totalEnergyUsed), 16, GAUGE_USED)

        #print(maxEnergyNeeded, totalEnergyNeeded, totalEnergyAvailable,totalEnergyUsed)

        # Plot graph of most recent values
        if maxEnergyNeeded>0:
            graph.axes(0,143,0,maxEnergyNeeded)
            graph.plot(dataNeeded, GAUGE_NEEDED)
            graph.plot(dataUsed, GAUGE_USED)        

        # Draw devices indicators
        for i,device in enumerate(devices.values()):
            #print(device)
            color = DEVICE_OFF if not device["on"] else DEVICE_ON if device["on"] and device["powered"] else DEVICE_NOPOWER
            pygame.draw.rect(screen, color, (10,indicatorsTop+(barheight+bargap)*i,maxBar,barheight))
            textLeft(screen, 10, indicatorsTop+(barheight+bargap)*i,device["name"]+" "+str(device["power_needed"]))

        # Turn device on/off if clicked
        clicked = (mousey-indicatorsTop)//(barheight+bargap)
        if clicked>=0 and clicked<=len(devices):
            devices[list(devices.keys())[clicked]]["on"] = 1-devices[list(devices.keys())[clicked]]["on"]

    else:
        textLeft(screen, 10, 10, "Press RESET on your Microbit")

    # Update the display (flip the in-memory buffer on to the screen)
    #print("flip")
    pygame.display.flip()


microbit.disconnect()

# Done! Time to quit.
pygame.quit()