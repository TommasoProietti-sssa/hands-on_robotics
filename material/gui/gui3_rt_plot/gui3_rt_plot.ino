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
   
    // print to serial
    Serial.println(random(0,10));
    
    // update timing variables
    previous_time = current_time; 
  }
}
