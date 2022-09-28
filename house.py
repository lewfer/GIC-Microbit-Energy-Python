"""
house.py

Interfaces between Microbit controlling the house and the web service (national grid).
Also provides a UI to show what's happening in the house.

Reads available energy from the national grid and turns on whatever devices can be powered.
"""

# Setup
###################################################################################################


# Define the devices we need to power
# These will be populated by the microbit
devices = {}
"""
devices = [{"name":"light", "power_needed":100, "on":1, "powered":0}, 
           {"name":"toaster","power_needed":100, "on":1, "powered":0}, 
           {"name":"car","power_needed":100, "on":1, "powered":0}, 
           {"name":"tv","power_needed":100, "on":1, "powered":0}, 
           {"name":"dishwasher","power_needed":100, "on":1, "powered":0}]
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

# Run until the user asks to quit
running = True

# Set to true when microbit is ready
ready = False

# Main
###################################################################################################

# Pygame window parameters
windowWidth = 500
windowHeight = 500
maxBar = windowWidth-20
mousex = 0
mousey = 0

# Object to connect to microbit
microbit = Microbit(house_serialport)
microbit.connect()


# Function to listen for serial messages from the microbit
# This will run on a separate thread to the pygame loop
def listen():
    global ready

    while running:
        try:
            message = microbit.read()
            print("new message",message)

            if message=="clear":
                print("Receive:","clear")
                devices.clear()

            elif message.startswith("debug"):
                print(message)

            elif message=="get":
                for device in devices.values():
                    if device["on"] and device["powered"]:
                        message = f"{device['name']}=1\n"
                    else:
                        message = f"{device['name']}=0\n"
                    #message += "\n"
                    microbit.write(message)
                    print("Sending:",message)     

            elif message=="ready":           
                ready = True

            elif message.startswith("get"):
                split = message.split("=")
                device = devices[split[1]]
                if device["on"] and device["powered"]:
                    status = "1\n"
                else:
                    status = "0\n"
                microbit.write(status)
                print("Sending:",status)   

            elif (len(message)>0):
                print("Receive:",message)
                split = message.split("=")
                devices[split[0]] = {"name":split[0], "power_needed":int(split[1]), "on":0, "powered":0}
        except Exception as e:
            print(e)
            pass


# Create a new thread for the listen function
Thread(target=listen).start()


# Startup pygame window
pygame.init()
screen = pygame.display.set_mode([windowWidth, windowHeight])

DRAWENERGY= pygame.USEREVENT + 1 
pygame.time.set_timer(DRAWENERGY, 5000)

totalEnergyNeeded = 0
totalEnergyAvailable = 0



# Main Pygame loop
while running:

    # Did the user click the window close button?
    mousex = -1
    mousey = -1
    drawEnergy = False 
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.MOUSEBUTTONDOWN:
            pos = pygame.mouse.get_pos()
            mousex, mousey = pos
        if event.type == DRAWENERGY:
            drawEnergy = True

    # Fill the background with white
    screen.fill((255, 255, 255))       

    # Work out total energy needed by the devices
    totalEnergyNeeded = 0
    for device in devices.values():
        devicePowerNeeded = device["power_needed"]
        totalEnergyNeeded += devicePowerNeeded
    #print("totalEnergyNeeded",totalEnergyNeeded)


    if ready:
        if drawEnergy:


            # Find out how much energy is available at the national grid
            url = "http://lewfer.pythonanywhere.com/gettotalenergy"
            response = requests.get(url)
            totalEnergyAvailable = int(response.json())
            #print("Available:", totalEnergyAvailable)

            # Power each device (turn on "powered") until we run out of energy
            totalEnergyUsed = 0
            for device in devices.values():
                if device["on"]:
                    devicePowerNeeded = device["power_needed"]
                    if devicePowerNeeded <= totalEnergyAvailable:
                        device["powered"] = 1
                        totalEnergyUsed += devicePowerNeeded
                        totalEnergyAvailable -= devicePowerNeeded
                    else:
                        device["powered"] = 0
            #print(f"Total energy used {totalEnergyUsed}")

            # Tell National Grid how much we used
            url = f"http://lewfer.pythonanywhere.com/use?energy={totalEnergyUsed}"
            response = requests.get(url)
            #print(response.json())

            # Tell microbit which devices to turn on or off
            #message = ""
            """
            for device in devices:
                if device["on"] and device["powered"]:
                    message = f"{device['name']}=1\n"
                else:
                    message = f"{device['name']}=0\n"
                #message += "\n"
                microbit.write(message)
                print("Sending:",message)
            """

            #print(devices)

            #print("write")
            #totalEnergy = random.randrange(0,200)
            #print(totalEnergy)
            #microbit.write(f"{totalEnergy}\n")


        # Draw bar to show avail energy vs needed energy
        bar = maxBar if totalEnergyNeeded==0 else map(min(totalEnergyNeeded*2,totalEnergyAvailable), 0, totalEnergyNeeded*2, 0, maxBar)
        color = red if totalEnergyAvailable<totalEnergyNeeded else yellow if totalEnergyAvailable<totalEnergyNeeded*1.5 else green
        pygame.draw.rect(screen, red, (10,10,maxBar/2,50))    
        pygame.draw.rect(screen, yellow, (10+maxBar/2,10,maxBar/4,50))    
        pygame.draw.rect(screen, green, (10,10,bar,50))  
        #pygame.draw.rect(screen, color, (10,10,bar,50))    
        pygame.draw.rect(screen, black, (10,10,maxBar/2,50), 2)
        textLeft(screen, 10, 10, "Avail:"+str(totalEnergyAvailable))
        textLeft(screen, 10, 30, "Needed:"+str(totalEnergyNeeded))

        # Draw devices indicators
        barheight = 30
        bargap = 2
        for i,device in enumerate(devices.values()):
            color = grey if not device["on"] else green if device["on"] and device["powered"] else pygame.Color("cadetblue1")
            pygame.draw.rect(screen, color, (10,100+(barheight+bargap)*i,maxBar,barheight))
            textLeft(screen, 10, 100+(barheight+bargap)*i,device["name"])

        clicked = (mousey-100)//(barheight+bargap)
        #print("Clicked",clicked)
        if clicked>=0 and clicked<=len(devices):
            devices[list(devices.keys())[clicked]]["on"] = 1-devices[list(devices.keys())[clicked]]["on"]

        

    # Update the display (flip the in-memory buffer on to the screen)
    #print("flip")
    pygame.display.flip()


microbit.disconnect()

# Done! Time to quit.
pygame.quit()