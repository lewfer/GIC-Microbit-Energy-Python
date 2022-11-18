"""
powerstation.py

Interfaces between Microbit controlling the powerstation and the web service (national grid).
Also provides a UI to show what's happening in the powerstation.

Reads energy from wind and solar and sends to the national grid.
"""



# Imports
###################################################################################################

# Import and initialize the pygame library
import pygame
from pygame.locals import *
import serial
#from random import randint
from time import sleep
import requests
from microbit import *
from utils import *
from settings import *
import time

# Main
###################################################################################################

# Data logging
dataWind = []
dataSolar = []

# Object to connect to microbit
microbit = Microbit(powerstation_serialport)
microbit.connect()

# Startup pygame window
pygame.init()
screen = pygame.display.set_mode([500, 500])

# Create objects on the screen
b = Button (150,450,100,50, "Stop")
graph = Graph(100,100,300,300, screen)

# Run until the user asks to quit
running = True

wind,solar,total = 0,0,0

# Main Pygame loop
while running:

    c =  False
    # Did the user click the window close button?
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.MOUSEBUTTONUP:
            clicked = pygame.mouse.get_pos()

            if b.clicked(clicked):
                c = True

    # Fill the background with white
    screen.fill((255, 255, 255))

    # Read values from Microbit
    reading = microbit.read()
    print(reading)

    # Decode the reading
    
    if len(reading)>=7 and reading[0]=="#" and reading[-1]==".": # check we have a valid reading
        # Attempt to decode values
        try:
            wind,solar,total = reading[1:-1].split(",")
            wind = int(wind)
            solar = int(solar)
            total = int(total)

            if wind+solar==total:
                # Add values to history
                dataWind.append(wind)
                dataSolar.append(solar)
                dataWind = dataWind[-144:]
                dataSolar = dataSolar[-144:]

                start = time.time()
                url = grid_url + f"/add?station={station_name}&wind={wind}&solar={solar}"
                response = requests.get(url)
                end = time.time()
                print("Time", end - start)
                #print(response.json())
            else:
                print("err")
        except ValueError:
            pass
    

    # Display values on screen
    textLeft(screen, 10,10,f"Wind:{wind}")
    textLeft(screen, 10,30,f"Solar:{solar}")

    if c:
        text(screen, 150,450,"clicked")

    # Plot graph of most recent values
    graph.axes(0,143,0,200)
    graph.plot(dataWind, red)
    graph.plot(dataSolar, blue)

    # Draw button
    b.draw(screen, True)

    #sleep(1)

    #mouse = pygame.mouse.get_pos()

    # Update the display (flip the in-memory buffer on to the screen)
    pygame.display.flip()

microbit.disconnect()

# Done! Time to quit.
pygame.quit()