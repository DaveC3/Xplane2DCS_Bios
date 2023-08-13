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
import threading


nav1_Mhz_lookup ={
    '108': 0,
    '109': 1,
    '110': 2,
    '111': 3,
    '112': 4,
    '113': 5,
    '114': 6,
    '115': 7,
    '116': 8,
    '117': 9
    }
nav1_Khz_lookup = {
    '00': 0,
    '05': 1,
    '10': 2,
    '15': 3,
    '20': 4,
    '25': 5,
    '30': 6,
    '35': 7,
    '40': 8,
    '45': 9,
    '50': 10,
    '55': 11,
    '60': 12,
    '65': 13,
    '70': 14,
    '75': 15,
    '80': 16,
    '85': 17,
    '90': 18,
    '95': 19    
    }

TAC_ones = [0,1,2,3,4,5,6,7,8,9] 
TAC_tens = [0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19]  
Ils_Mhz = [0,1,2,3,4,5,6,7,8,9] 
Ils_Khz= [0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19] 

tacan_ones_pos = 0
tacan_tens_pos = 0
ILS_Khz_pos = 0
ILS_Mhz_pos = 0
tac = 0
Khz = 0
Mhz = 0
tac_old = 0
Khz_old = 0
Mhz_old = 0
valuesOLD = 0


def rec_UDP():
    print("MAIN")
  # Open a Socket on UDP Port 49000
    UDP_IP ="127.0.0.1"
    UDP_PORT = 49001
    sock = socket.socket(socket.AF_INET, # Internet
                       socket.SOCK_DGRAM) # UDP
    sock.bind((UDP_IP, UDP_PORT))  #Xplane
    #sock.bind(("192.168.1.188", 5010)) # DCS
    print("bound")

    while True:
        
        data, addr = sock.recvfrom(1024) # buffer size is 1024 bytes
        DecodeUDP_Packet(data)
#         time.sleep(1)
#         print(data)

def DecodeUDP_Packet(data):
  # Packet consists of 5 byte header and multiple messages. 
  #debug by uncommenting next line
#     print("raw data-> %s" % data, end="\r", flush=False)
#    index = 0  
#    buff = []	#bytearray(41)
    valuesout = {data}
    headerlen = 5
    header = data[0:headerlen]
    #valueHeader = (struct.unpack("4s",data[0:5]))
    #assert idx == index
     #List slicing           
    messages = data[5:]
    lenmesg = (len(messages))
    if(header==b'DATA*'):
       
    # Divide into 36 byte messages
        messagelen = 36
    #print("Processing")
        for i in range(0,int((len(messages))/messagelen)):
            message = messages[(i*messagelen) : ((i+1)*messagelen)]
            DecodeDataMessage(message)
#             valuesout.update( values )
    else:
        print("THIS packet type not implemented. ")

    return valuesout



def DecodeDataMessage(message):
  # Message consists of 4 byte type and 8 times a 4byte float value.
  # Write the results in a python dict.
    global valuesOLD
    values = {}
    typelen = 4
    type = int.from_bytes(message[0:typelen], byteorder='little')
    data = message[typelen:]
    dataFLOATS = struct.unpack("<ffffffff",data)


    if type == 96:
        values["Com1"]=dataFLOATS[0]

    elif type == 97:
        values=dataFLOATS[0]
        if values != valuesOLD:
        
            myinteger = values
            val_string = str(myinteger)
            
    #         print(values)
            #values = values * 10
            pMhz = val_string[:3]
            pKhz = val_string[3:5]
    #         print(pMhz,".", pKhz)
    #         Mhz = int(values[:3])
    #         Khz = int(values[3:5])        
            Mhz= (nav1_Mhz_lookup[pMhz])
            Khz =(nav1_Khz_lookup[pKhz])
            tac = 5
            print(Mhz,Khz)
            valuesOLD = values
            updateDisp(tac, Khz,Mhz)




def updateDisp(tac, Khz,Mhz):
#     print("Tacan 1s  = ",tac, "Ils Khz = ",Khz, "Ils Mhz = ",Mhz)
    global tac_old 
    global Khz_old 
    global Mhz_old
    if tac == None :
        tac = tac_old     
    
    if Khz == None:
        Khz =Khz_old
        
    if Mhz == None:
        Mhz =Mhz_old       
    
    if tac != tac_old :
        tac = tac << 10
        tac_old = tac
        
    if Khz != Khz_old:
        Khz = Khz << 4
        Khz_old = Khz
        
    if Mhz != Mhz_old :
        Mhz = Mhz
        Mhz_old = Mhz
        
#     print( "Ils Khz = ",Khz, "Ils Mhz = ",Mhz)
    data = (Mhz + Khz+ tac)
#     print(data)
    data = data.to_bytes(2, 'little')
    packet = b'UUUU'
    packet = packet + b":\x90\x02\x00"
    packet = packet + data
    packet = packet + b"\x02\x00\x00\x3c'"
#     print(packet)
    time.sleep(.2)
#     print(packet)
    mWindow.ser.write(packet)
    



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
#class master(tk.Tk):
# class StringDisplay:
# 
#     def __init__(self, frame, name, address, mask):
# 
#         self.f = tk.LabelFrame(frame, text=name)
#         self.f.grid( row = 1 + int( mWindow.widgetCount/2), column = int(mWindow.widgetCount % 2) )
# 
#         self.myText = StringVar()
#         self.currentText = ""
#         self.e = tk.Entry(self.f , width=20, textvariable=self.myText)
#         self.e.pack(side=LEFT) 
# 
#         self.b = tk.Button(self.f, text='>', command=self.ButtonPress, width=1)
#         self.b.pack(side=LEFT) 
# 
#         self.address = address
#         self.max_length = mask
#         self.count = 0
#         self.changed = 0
# 
#     def __del__(self):
#         print("Destroying")
#         self.f.destroy()
# 
#     def ButtonPress(self) :
#         print("String Element ")
#         v = self.myText.get() + "                  "
#         self.currentText = v.encode()
#         #self.currentText = self.currentText[0:self.max_length]
#         print(self.currentText)
#         self.changed = 1
#         self.count = 0
#         self.updateAddr = self.address
# 
# 
#     def getPacket(self) :
#         packet = ""
#         if self.changed :
#             toSend = (self.address + self.max_length) - self.updateAddr
#             if toSend > 4 :
#                 toSend = 4
#             if toSend == 1 :
#                 toSend = 2 		#always pad to 2 bytes
#             if toSend >= 1:
#                 v = self.currentText[self.count:self.count + toSend] 
#                 #+ b" "
#                 
# 
#                 l = b"" + np.uint8(toSend%256) + np.uint8(toSend/256)
#                 packet =  b"" + np.uint8(self.updateAddr%256) + np.uint8(self.updateAddr/256) + l + v
#                 self.count = self.count + toSend
#                 self.updateAddr = self.updateAddr + toSend
#                 if self.updateAddr >= self.address + self.max_length :
#                     self.changed = 0
# 
#                 
# 
#             
#         print(len(packet))
#         print(packet)
#         return packet        
        
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


        master.title("X-Plane to DCS TACAN/ILS")
        #master.geometry("450x350")
        # Create text widget and specify size.



               #Controls
        self.intervalF = Frame(self.topF)
        self.intervalF.pack(side=LEFT)

        self.noUpdates = IntVar()
        self.intervalE = tk.Entry(self.intervalF, width=2, textvariable=self.noUpdates)
        self.intervalE.grid(row=0, column=1)


        self.findSerPortsB = tk.Button(self.topF, text="Find Serial Ports")
        self.findSerPortsB.bind("<Button-1>", self.findSerPorts)
        self.findSerPortsB.pack(side=LEFT)
        
                #Recv Data 
        self.rightF = tk.LabelFrame(self.mainF, height = 30, text="Recv Text", width=50)
        self.rightF.grid(row=0, column=0, rowspan=20)

        #Recv Data
        
        self.recvTextVariable = StringVar()
        self.recvText = tk.Label(self.rightF, textvariable = self.recvTextVariable, height=40, width = 30,  anchor=NW, justify=LEFT)
        self.recvText.pack(anchor=N)



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
    def start_UDP(self, event):
        rec_UDP()
    #######################################
#packet = packet + b"\xFE\xFF\x02\x00" + np.uint8(mWindow.updateCount%256) + b"\x00"    
      
  
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
    
###############################################


####################################################
     
# 
root = tk.Tk()
mWindow = DCSMainWindow(root) 


#update()

root.mainloop()
rec_UDP()
print("Exiting")