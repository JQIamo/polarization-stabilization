//Define pins for input here
int pin1 = 14;
int pin2 = 15;
int pin3 = 16;
int pin4 = 17;
int pin5 = 18;
int pin6 = 19;

//unsigned long samples = 10000*10;
unsigned long Tstart;
unsigned long Tstop;
void setup() {
  // put your setup code here, to run once:
  Serial.begin(115200);
  pinMode(pin1, INPUT);
  pinMode(pin2, INPUT);
  pinMode(pin3, INPUT);
  pinMode(pin4, INPUT);
  pinMode(pin5, INPUT);
  pinMode(pin6, INPUT);
}

void loop() {
  if(Serial.available()>0){
      unsigned int samples = Serial.readString().toInt();
      unsigned int i = 0;
       union data_union {
       struct data_struct{
        int startChar;
        unsigned int timeStamp;
        int V1;
        int V2;
        int V3;
        int V4;
        int V5;
        int V6;
        int endChar;
        } data;
        char buf[sizeof(data)];
       } record;

       record.data.startChar = -100;
       record.data.endChar = -200;
       Tstart = millis();
       
      while(i < samples){
        record.data.timeStamp = micros();
        record.data.V1 = analogRead(pin1);
        record.data.V2 = analogRead(pin2);
        record.data.V3 = analogRead(pin3);
        record.data.V4 = analogRead(pin4);
        record.data.V5 = analogRead(pin5); 
        record.data.V6 = analogRead(pin6);
        Serial.write(record.buf,sizeof(record.data));
        i++;
      }
    }

}
