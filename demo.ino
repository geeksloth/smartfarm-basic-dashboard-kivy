#include <Wire.h>
#include <LiquidCrystal_I2C.h>

LiquidCrystal_I2C lcd(0x27, 16, 2);

const int soilPin = A0;
const int rainPin = A1;
const int vrPin = A2;
const int inputPin = 2;
const int ledPin = 13;

void setup() {
  // put your setup code here, to run once:
  Serial.begin(9600);
  lcd.init();
  lcd.backlight();
  //lcd.setCursor(0,0);
  //lcd.print("Farm IoT Demo");
  pinMode(inputPin, INPUT);
  pinMode(ledPin, OUTPUT);
}

void loop() {
  int state = digitalRead(inputPin);
  digitalWrite(ledPin, state);

  int soil = readSoilModule();
  int rain = readRainModule();
  int vr = readVrModule();

  displayLCD(soil, rain, vr);
  sendSerial(soil, rain, vr);
  delay(500);
}

void sendSerial(int soil, int rain, int vr){
  Serial.print("soil:");
  Serial.print(soil);
  Serial.print(";");
  Serial.print("rain:");
  Serial.print(rain);
  Serial.print(";");
  Serial.print("vr:");
  Serial.println(vr);
}
void displayLCD(int soil, int rain,int  vr){
  lcd.setCursor(0,0);
  lcd.print("Soil");
  lcd.print(soil);
  lcd.print(" VR");
  lcd.print(vr);
  lcd.print("   ");
  
  lcd.setCursor(0,1);
  lcd.print("Rain");
  lcd.print(rain);
  lcd.print("   ");
}

int readSoilModule(){
  int soilValue = analogRead(soilPin);
  return soilValue;
}

int readRainModule(){
  int rainValue = analogRead(rainPin);
  return rainValue;
}

int readVrModule(){
  int vrValue = analogRead(vrPin);
  return vrValue;
}