


#define DCSBIOS_IRQ_SERIAL
//#define DCSBIOS_DEFAULT_SERIAL
//#define LIBCALL_ENABLEINTERRUPT

#include <DcsBios.h>
#include <SPI.h>
#include <Wire.h>
#include <Adafruit_GFX.h>
#include <Adafruit_SH1106.h>
#include <LedControl.h>
#define OLED_RESET 4
Adafruit_SH1106 display(OLED_RESET);
LedControl lc=LedControl(17,15,16,1); //This creates an instance of a single controller named "lc"
/*
 * Vcc green
 * GND yellow
 * DIN orange  17
 * CS  red     16
 * CLK brown   15
 */

bool Zero = false;
String str_freq ;
String hi_freq;
String low_freq;
String lowNav_freq;
String HiNav_Freq;
String freq;
unsigned long lastMilli = 0;
int8_t TensDisp[2];
int incomingByte = 0; // for incoming serial data
//-------------------------- Tacan Ones display ---------------------------------------

void onTacanChan1Change(unsigned int newValue) {
  low_freq = newValue;
    drawchar();
}

DcsBios::IntegerBuffer tacanChan1Buffer(0x903a, 0x3c00, 10, onTacanChan1Change);
//--------------------------- Tacan 10s Display --------------------------------------

void onTacanChan10Change(unsigned int newValue) {
      if(newValue < 10){
        Zero = true;
      }else{
        Zero = false;
      }
      hi_freq = newValue ;   //TensDisp[0]+TensDisp[1]; 
      drawchar();
}

DcsBios::IntegerBuffer tacanChan10Buffer(0x903c, 0x001f, 0, onTacanChan10Change);
//------------------------------- Print Tacan frequency ---------------------------
void drawchar(void) {
 display.clearDisplay();
 // String Freq = hi_freq + low_freq;
  display.setTextSize(7);
  display.setTextColor(WHITE);
  display.setCursor(0, 0);
  if(Zero == true){
    display.print("0");
  }
  display.print(hi_freq + low_freq);
  display.display();
}

//------------------------------- NAV Mhz ----------------------------------

void onVorIlsFreq1Change(unsigned int newValue) {
      HiNav_Freq=String(newValue+108);
 //     HiNav_Freq = String(newValue);  //123.xxx
      lc.setChar(0,5,HiNav_Freq[0],false);
      delay(100);
      lc.setChar(0,4,HiNav_Freq[1],false);
      delay(100);
      lc.setChar(0,3,HiNav_Freq[2],true);
  
  
  }
  
  DcsBios::IntegerBuffer vorIlsFreq1Buffer(0x903a, 0x000f, 0, onVorIlsFreq1Change);


//---------------------------------- NAV Khz --------------------------
void onVorIlsFreq50Change(unsigned int newValue){
          lowNav_freq = String(newValue*5);  // XXX.11
          lc.setChar(0,2,lowNav_freq[0],false);
          lc.setChar(0,1,lowNav_freq[1],false);


}
DcsBios::IntegerBuffer vorIlsFreq50Buffer(0x903a,0x01f0,4,onVorIlsFreq50Change);

//-----------------------------------------------------------------
// depending on encoder steps per detent need to change
//namespace DcsBios {
//  enum StepsPerDetent {
//    ONE_STEP_PER_DETENT = 1,
//    TWO_STEPS_PER_DETENT = 2,
//    FOUR_STEPS_PER_DETENT = 4,
//    EIGHT_STEPS_PER_DETENT = 8,
//  };
//
//  template <unsigned long pollIntervalMs = POLL_EVERY_TIME, StepsPerDetent stepsPerDetent = TWO_STEPS_PER_DETENT>
//D:\Documents\Arduino\libraries\dcs-bios-arduino-library-master\src\internal\encoder.h

DcsBios::RotaryEncoder tacanChan1("TACAN_CHAN_1", "DEC", "INC", 3, 2);
DcsBios::RotaryEncoder tacanChan10("TACAN_CHAN_10", "DEC", "INC", 5, 4);
DcsBios::RotaryEncoder vorIlsFreq1("VOR_ILS_FREQ_1", "DEC", "INC", 9, 8);
DcsBios::RotaryEncoder vorIlsFreq50("VOR_ILS_FREQ_50", "DEC", "INC", 7, 6);


//DcsBios::Switch2Pos tacanPw("TACAN_PW", PIN);
//-----------------------------------------------------------------
void setup() {
  DcsBios::setup();
  // by default, we'll generate the high voltage from the 3.3v line internally! (neat!)
  display.begin(SH1106_SWITCHCAPVCC, 0x3C);  // initialize with the I2C addr 0x3D (for the 128x64)
//  display.display();
//  delay(2000);
  // Clear the buffer.
  display.clearDisplay();
  delay(2000);
  display.clearDisplay();
  display.setTextSize(2);
  display.setTextColor(WHITE);
  display.setCursor(0, 0);
  display.println("T-45 TACAN");
  display.display();
  delay(2000);
  display.clearDisplay();
  hi_freq = String(17);
  low_freq = String(2);
  drawchar();
//FIRST - 8 DIGIT 7 SEGMENT DISPLAY - VHF-AM RADIO (CODE) MAX7219 INITIALISATION
lc.shutdown(0,false); //turn on the display
lc.setIntensity(0,8);//set the brightness 
lc.setScanLimit(0,5); //Set the number of digits (or rows) to be displayed.
lc.clearDisplay(0); //clear the display 

//FIRST - 8 DIGIT 7 SEGMENT DISPLAY - VHF-AM RADIO (CODE) MAX7219 BOOT CODE WHILST AWAITING SOCAT DATA STREAM
// 
freq = String(1117500);
//sprintf(buffer, "%d", freq);  
lc.setChar(0,6,freq[0],false);
delay(100);
lc.setChar(0,5,freq[1],false);
delay(100);

lc.setChar(0,4,freq[2],false);
delay(100);
lc.setChar(0,3,freq[3],true);
delay(100);
lc.setChar(0,2,freq[4],false);
delay(100);
lc.setChar(0,1,freq[5],false);
delay(2000);

}
//-----------------------------------------------------------------
void loop() {
  DcsBios::loop();
//  if (Serial.available() > 0) {
//     // read the incoming byte:
//     incomingByte = Serial.read();

//     // say what you got:
//     Serial.print("I received: ");
//     Serial.println(incomingByte, DEC);
//  }
//  if (millis() - lastMilli < 40) {
//    return;
//  }
//
//
//  lastMilli = millis();
}
//-----------------------------------------------------------------
