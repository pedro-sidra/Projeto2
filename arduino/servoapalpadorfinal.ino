#include<Servo.h>;
#define SERVO 6

Servo servo;
char cmd;

void setup() {
   Serial.begin(9600);
   servo.attach(SERVO,544,1990);
}

void loop() {
  while(!Serial.available());
  cmd=Serial.read();
  switch (cmd)
  {
    case 's':
      //Serial.println("oi");
      servo.write(0);
      delay(200);
      break;
    case 'd':
      //Serial.println("tchau");
      servo.write(180);
      delay(200);
      break;
    case 'k':
      //Serial.println("killing");
      servo.detach();
      delay(200);
      break;
    case 'r':
      //Serial.println("revive");
      servo.attach(SERVO,544,1990);
      delay(200);
      break;
    default:
      break;
  }
}

  

