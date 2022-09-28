import serial

class Microbit():
    def __init__(self, serialport):
        self.serialport = serialport

    def connect(self):
        #self.serial = serial.Serial(self.serialport, 115200,  parity=serial.PARITY_NONE, stopbits=serial.STOPBITS_ONE, timeout=10)
        self.serial = serial.Serial(self.serialport, 9600,  parity=serial.PARITY_NONE, stopbits=serial.STOPBITS_ONE, timeout=10)


    def disconnect(self):
        self.serial.close()

    def read(self):
        try:
            line = self.serial.readline().decode("utf-8").strip()
        except:
            line = ""
        return line

    def write(self, message):
        self.serial.write(message.encode('utf-8'))


