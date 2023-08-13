

/*
  Tell DCS-BIOS to use a serial connection and use interrupt-driven
  communication. The main program will be interrupted to prioritize
  processing incoming data.
  
  This should work on any Arduino that has an ATMega328 controller
  (Uno, Pro Mini, many others).
 */
#define DCSBIOS_IRQ_SERIAL
#include <LedControl.h>
#include "DcsBios.h"


String str_freq;
String hi_freq;
String low_freq;
String lowdig_freq;
String freq;
LedControl lc=LedControl(15,16,17,1); //This creates an instance of a single controller named "lc"

// GENERAL REF NOTE BELOW
/*
The sequence of pins used above are in the following order... LedControl(DIN,CLK,LOAD,# OF IC's) 
pin 15 (A1) is connected to the DataIn 
pin 16 (A2) is connected to the CLK 
pin 17 (A3)is connected to LOAD
the last number...(1) is for how many MAX7219 we have daisy chained. (8 STATED, HOWEVER 4 ACTUALLY PRESENT)
*/


//----------------------------------------------------------------------------------
void onComm1HighFreqChange(unsigned int newValue) {
//    /* your code here */
      hi_freq = String(newValue);  //123.xxx
      lc.setChar(0,6,hi_freq[0],false);
      delay(100);
      lc.setChar(0,5,hi_freq[1],false);
      delay(100);
      lc.setChar(0,4,hi_freq[2],false);

}
DcsBios::IntegerBuffer comm1HighFreqBuffer(0x902a, 0x1ff0, 4, onComm1HighFreqChange);
//----------------------------------------------------------------------------------
void onComm1Dial3FreqChange(unsigned int newValue) {
//    /* your code here */
          low_freq = String(newValue);  // XXX.1xx
          lc.setChar(0,3,low_freq[0],false);

}
DcsBios::IntegerBuffer comm1Dial3FreqBuffer(0x902a, 0x000f, 0, onComm1Dial3FreqChange);

//----------------------------------------------------------------------------------
void onComm1Dial4FreqChange(unsigned int newValue) {
//    /* your code here */
          lowdig_freq = String(newValue);  // XXX.X11
          lc.setChar(0,2,lowdig_freq[0],false);
          lc.setChar(0,1,lowdig_freq[1],false);
}

DcsBios::IntegerBuffer comm1Dial4FreqBuffer(0x901e, 0xfe00, 9, onComm1Dial4FreqChange);

//----------------------------------------------------------------------------------
//const byte comm1ModePins[3] = {11, 12, 14};


DcsBios::Switch3Pos comm1Freq10("COMM_1_FREQ_10", 2, 3);       //11X.XXX
DcsBios::Switch3Pos comm1Freq1("COMM_1_FREQ_1", 4, 5);         //XX1.XXX
DcsBios::Switch3Pos comm1Freq010("COMM_1_FREQ_010", 6, 7);     //XXX.1XX
DcsBios::Switch3Pos comm1Freq100("COMM_1_FREQ_100", 8, 9);     //XXX.X11

//DcsBios::RotaryEncoder<2> comm1Mode("COMM_1_MODE", "DEC", "INC", 10, 11);
DcsBios::Switch2Pos comm1Amfm("COMM_1_AMFM", 12);

//----------------------------------------------------------------------------------


//----------------------------------------------------------------------------------


void setup() {
  DcsBios::setup();
// MAX7219 INITIALISATION
//This initializes the MAX7219 and gets it ready for use:

//FIRST - 8 DIGIT 7 SEGMENT DISPLAY - VHF-AM RADIO (CODE) MAX7219 INITIALISATION
lc.shutdown(0,false); //turn on the display
lc.setIntensity(0,8);//set the brightness 
    //void setScanLimit(0,6); //Set the number of digits (or rows) to be displayed.
lc.clearDisplay(0); //clear the display 

//FIRST - 8 DIGIT 7 SEGMENT DISPLAY - VHF-AM RADIO (CODE) MAX7219 BOOT CODE WHILST AWAITING SOCAT DATA STREAM
// 
freq = String(12345678);
//sprintf(buffer, "%d", freq);  
lc.setChar(0,6,freq[0],false);
delay(100);
lc.setChar(0,5,freq[1],false);
delay(100);
lc.setChar(0,4,freq[3],false);
delay(100);
lc.setChar(0,3,freq[4],false);
delay(100);
lc.setChar(0,2,freq[5],false);
lc.setChar(0,1,freq[6],false);
//lc.setChar(0,0,'H',false);
}

void loop() {
  DcsBios::loop();
}
