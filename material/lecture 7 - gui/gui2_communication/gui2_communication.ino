#include <String.h>

int counter1 = 0;
int counter2 = 0;
int counter3 = 0;

String user_input;
int tmp;

// sample frequency
#define FREQ 200 // sampling frequency in Hz
unsigned long previous_time;
unsigned long current_time;
const unsigned long period = 1000/FREQ;

// the setup function runs once when you press reset or power the board
void setup() {
  Serial.setTimeout(1); // ms, remove delay in serial communication between feather and pyqt (default 1000ms)
  Serial.begin(9600);
  while(!Serial);
  previous_time = millis();  //initial start time
}

// the loop function runs over and over again forever
void loop() {
  current_time = millis();
  if (current_time - previous_time >= period) 
  {
    // read from serial
    if(Serial.available()){
      user_input = Serial.readStringUntil('\r\n');  // \r\n "passo e chiudo"
      tmp = user_input.toInt();
      if(tmp == 1){counter1++;}
      else if(tmp ==2){counter2++;}
      else{counter3++;}
    }
    else{
      user_input = "";
    }
    
    // print to serial
    Serial.print(counter1);
    Serial.print(",");
    Serial.print(counter2);
    Serial.print(",");
    Serial.print(counter3);
    Serial.println(",");
    
    // update timing variables
    previous_time = current_time; 
  }
}
