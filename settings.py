# settings.py
###################################################################################################

# Set the ports that the powerstation and house microbits are connected to
# On windows go to device manager then ports
# On Mac and linux, from a terminal type ls /dev/ttyACM*

# URL for the national grid web service
# Don't use 'localhost' here.  It can be painfully slow
grid_url = "http://127.0.0.1:8000"
#grid_url = "http://lewfer.pythonanywhere.com"

# Name of the power station
station_name = "Panda Power"
#station_name = "Eagle Energy"
#station_name = "Rhino Renewables"
#station_name = "Swan Sustainables"
#station_name = "Gecko Green Energy"

#station_name = "Possum Power"
#station_name = "Emu Energy"
#station_name = "Robin Renewables"
#station_name = "Stingray Sustainables"
#station_name = "Gazelle Green Energy"

# Serial ports to which microbit is attached
# On Windows look this up in Device Manager.  E.g. 'COM4'
# On Mac or Linux run 'ls /dev/tty*' from a terminal.  Use the full name, e.g. /dev/tty.usbmodel141302
powerstation_serialport = "COM4"
house_serialport = "COM8"