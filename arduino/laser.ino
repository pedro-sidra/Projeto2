#include<Servo.h>;

char cmd;

void setup() {
   Serial.begin(9600);
   
   pinMode(13, OUTPUT);
}

void loop() {
  while(!Serial.available());
  cmd=Serial.read();
  switch (cmd)
  {
    case 'l':
      //Serial.println("oi");
      digitalWrite(13, LOW);
      delay(200);
      break;
    case 'o':
      //Serial.println("tchau");
      digitalWrite(13, HIGH);
      delay(200);
      break;
    default:
      break;
  }
}
