# com27 is chair radio
APP_VERSION = "V1.4.1 27/6/20"

APP_NAME = "X-Plane to DCS Gauges"

from os.path import expanduser
userHome = expanduser("~")

from tkinter import *
import tkinter as tk 
import numpy as np
import sys
import glob
import time
import serial
import re
import socket
import struct 

com1_Khz_pos = 0
com1_Mhz10_pos = 0
com1_Mhz1_pos = 0
hz = 0
Khz = 0
Mhz10 = 0
hz_old = 0
Khz_old = 0
Mhz10_old = 0
Mhz1_old = 0
valuesOLD = 0

########################### receive from xplane send to com radio DCS Bios #############################

def rec_UDP():
#
  # Open a Socket on UDP Port 49000
    UDP_IP ="127.0.0.1"
    UDP_PORT = 49001
    sock = socket.socket(socket.AF_INET, # Internet
                       socket.SOCK_DGRAM) # UDP
    sock.bind((UDP_IP, UDP_PORT))  #Xplane
    if run:
        
        data, addr = sock.recvfrom(1024) # buffer size is 1024 bytes
        DecodeUDP_Packet(data)
        root.after(100,rec_UDP)
    else:
        print('stop')
#----------------------------------------------------------------------------------------
def DecodeUDP_Packet(data):
  # Packet consists of 5 byte header and multiple messages. 

    valuesout = {data}
    headerlen = 5
    header = data[0:headerlen]
    messages = data[5:]
    lenmesg = (len(messages))
    if(header==b'DATA*'):
       
    # Divide into 36 byte messages
        messagelen = 36
    #print("Processing")
        for i in range(0,int((len(messages))/messagelen)):
            message = messages[(i*messagelen) : ((i+1)*messagelen)]
            DecodeDataMessage(message)
    else:
        print("THIS packet type not implemented. ")
    return valuesout
#--------------------------------------------------------------------------
def DecodeDataMessage(message):
  # Message consists of 4 byte type and 8 times a 4byte float value.
  # Write the results in a python dict.
    global valuesOLD
    values = {}
    typelen = 4
    type = int.from_bytes(message[0:typelen], byteorder='little')
    data = message[typelen:]
    dataFLOATS = struct.unpack("<ffffffff",data)

    if type == 6:
        values["Com1"]=dataFLOATS[0]

    elif type == 96:
        values=dataFLOATS[0]
        if values != valuesOLD:
        
            myinteger = values
            val_string = str(myinteger)
            
            print(val_string)
            pMhz10 = val_string[:3]
            pKhz = val_string[3:4]
            phz = val_string[4:6]
            print(pMhz10, pKhz,phz)
            valuesOLD = values
            updateDisp(phz, pKhz,pMhz10)


#-------------------------------------------------------------------
def updateDisp(hz, Khz,Mhz10):

    global Mhz10_old
    global Khz_old 
    global hz_old
    if hz == None :
        hz = hz_old     
    
    if Khz == None:
        Khz =Khz_old
        
       
    if Mhz10 == None:
        Mhz10 =Mhz10_old  
    
    if hz != hz_old :
        hz = int(hz)
        hz = hz << 9
        hz_old = hz
        
    if Khz != Khz_old:
        Khz = int(Khz)
        Khz = Khz 
        Khz_old = Khz


    if Mhz10 != Mhz10_old :
        Mhz10 = int(Mhz10)
        Mhz10 = Mhz10 << 4
        Mhz10_old = Mhz10
        

    data = (Mhz10+ Khz)
    print(data)
    data = data.to_bytes(2, 'little')
    packet = b'UUUU'
    packet = packet + b"*\x90\x02\x00"
    packet = packet + data
    packet = packet + b"\x02\x00\x00\x3c'"
    print(packet)
    time.sleep(.2)
    print(packet)
    mWindow.ser.write(packet)
    
    data2 = (hz)
    print(data2)
    data2 = data2.to_bytes(2, 'little')
    addr=36894
    addr= addr.to_bytes(2,'little')
    packet = b'UUUU'
    packet = packet + addr
    packet = packet + b"\x02\x00"
    packet = packet + data2
    packet = packet + b"\x02\x00\x00\x3c'"
    print(packet)
    time.sleep(.2)
    print(packet)
    mWindow.ser.write(packet)

################################  end receive from Xplanw and send Com Radio DCS BIOS ############


class StatusBar :

    def __init__(self, master):
        #self.tk.Label = tk.Label(self, bd=1, relief=SUNKEN, anchor=W)
        self.Label = tk.Label(master, anchor=W)
        self.Label.pack(side=BOTTOM, fill=X)


    def set(self, format, *args):
        self.Label.config(text=format % args)
        self.Label.update_idletasks()

    def clear(self):
        self.Label.config(text="")
        self.Label.update_idletasks()

        
class DCSMainWindow:
    
    connectionIsOpen = 0 
    serPorts = []
    ser = serial.Serial()
    tickCounter = 0
    nextUpdate = time.monotonic()
    updateCount = np.uint16(0)
    dcsBiosButtons = []
    dcsBiosAddressOrder = {}
    dcsBiosValues = {}
    dcsBiosUpdate = {}
    widgetCount = 0

    appSettings = {}
    appSettings['Active'] = {}
    instrumentList = {}
    instrumentList['Active'] = {}


    tick = 0;



        #Create Main Window 
    def __init__(self, master ):


        master.geometry("712x712")
        master.title(APP_NAME + " " + APP_VERSION)

        #controls
        self.topF = tk.Frame(master, relief="raised")
        self.topF.pack( anchor = W)

        self.mainF = tk.Frame(master)
        self.mainF.pack( anchor = W)
        
        self.statusBar = StatusBar(master)
        self.statusBar.set("%s", "Ready")


        master.title("X-Plane to DCS Com1")
        #master.geometry("450x350")
        # Create text widget and specify size.



               #Controls
        self.intervalF = Frame(self.topF)
        self.intervalF.pack(side=LEFT)

        self.findSerPortsB = tk.Button(self.topF, text="Find Serial Ports")
        self.findSerPortsB.bind("<Button-1>", self.findSerPorts)
        self.findSerPortsB.pack(side=LEFT)
        
        self.serialPortList =  serial_ports() 
        if len(self.serialPortList) == 0 :
            self.serialPortList = ["-"]
        print(self.serialPortList)

        self.serialPortChoice = StringVar()
        self.serialPortChoice.set("-")
        self.listB = OptionMenu(self.topF, self.serialPortChoice, *self.serialPortList)
        self.listB.pack(side=LEFT)
        
        self.connectButtonText = StringVar()
        self.connectButtonText.set("Connect")
        self.connectB = tk.Button(self.topF, textvariable=self.connectButtonText)
        self.connectB.bind("<Button-1>", self.toggleConnection)
        self.connectB.pack(side=LEFT)
        
        self.UDPButtonText = StringVar()
        self.UDPButtonText.set("Start UDP")
        self.UDPB = tk.Button(self.topF, textvariable=self.UDPButtonText)
        self.UDPB.bind("<Button-1>", self.start_UDP)
        self.UDPB.pack(side=LEFT)
        
        self.stopButtonText = StringVar()
        self.stopButtonText.set("Stop Receiving UDP")
        self.stopB = tk.Button(self.topF, textvariable=self.stopButtonText)
        self.stopB.bind("<Button-1>", self.stopLoop)
        self.stopB.pack(side=RIGHT)
        

    def findSerPorts(self,event) :
        print("Poll Serial")
        self.serialPortList =serial_ports() 

        print(self.serialPortList)
        if len(self.serialPortList) == 0 :
            self.serialPortList = ["-"]
        self.serialPortChoice.set("-")
        self.listB['menu'].delete(0, 'end') 
        
        for choice in self.serialPortList :
            self.listB['menu'].add_command(label=choice, command=tk._setit(self.serialPortChoice, choice))


    def toggleConnection(self,event):

        if self.connectionIsOpen :
            self.connectionIsOpen = 0
            print("Close Connection")
            self.connectButtonText.set("Connect")
            self.ser.close() 
            self.statusBar.set("%s", "Ready")
        else :
            
            print("Try to Open Connection on " + self.serialPortChoice.get() )
            
            if self.serialPortChoice.get() != "-" :
                try:
                    self.ser = serial.Serial(self.serialPortChoice.get(), 250000, timeout=0, rtscts=0)  # open serial port
                except:
                    self.ser = ""
                print(">" + str(self.ser) + "<")
                if self.ser == "" :
                    print("Failed")
                    print("No Serial Port Found/Accessible: Try another")

                else :
                    print("Successful")
                    self.connectionIsOpen = 1
                    self.nextUpdate = time.monotonic() + 1.5
                    self.connectButtonText.set("Close")
                    self.runUp = 3
                    self.statusBar.set("%s", "Connected to:" + self.serialPortChoice.get())
 
            else :
                print("Select a Serial Port")
#******************************************************************                
                
    def start_UDP(self, event):
        global run
        run = True
        rec_UDP()
#******************************************************************          
        
    def stopLoop(self,event):
        global run
        run=False
#******************************************************************
        
#     def checkRun():
#         run = run
      
  
def serial_ports():
# """ Lists serial port names
# 
#     :raises EnvironmentError:
#         On unsupported or unknown platforms
#     :returns:
#         A list of the serial ports available on the system
# """
    if sys.platform.startswith('win'):
        
        ports =['COM%s' % (i + 1) for i in range(100)]
    elif sys.platform.startswith('linux') or sys.platform.startswith('cygwin'):
        # this excludes your current terminal "/dev/tty"
        ports = glob.glob('/dev/tty[A-Za-z]*')
    elif sys.platform.startswith('darwin'):
        ports = glob.glob('/dev/cu.usb*')
    else:
        raise EnvironmentError('Unsupported platform')

    result = []
    for port in ports:
        print(port)
        try:
            s = serial.Serial(port)
            s.close()
            result.append(port)
            print(result)
        except (OSError, serial.SerialException):
            pass
    return result        
    

####################################################
 
root = tk.Tk()
mWindow = DCSMainWindow(root) 


#update()

root.mainloop()
rec_UDP()
print("Exiting")