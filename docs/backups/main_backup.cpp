// Carrinho Mecanum ESP32
// Controle via Dabble App - GamePad e Joystick

#include <Arduino.h>
#include "Config.h"
#include "MecanumDrive.h"
#include "ControleDabble.h"

MecanumDrive mecanumDrive;
ControleDabble* controleEntrada;

unsigned long lastStatusUpdate = 0;
bool systemInitialized = false;

void printWelcomeMessage() {
  Serial.println("ESP32 Carrinho Mecanum");
  Serial.printf("Bluetooth: %s\n", BT_DEVICE_NAME);
}

void printControlInstructions() {
  Serial.println("Controles disponiveis:");
  Serial.println("- Setas direcionais (GamePad)");
  Serial.println("- Joystick analogico");
  Serial.println("LED: Piscando=Pronto | Solido=Conectado");
}

void printSystemStatus() {
  DadosMovimento movimento = controleEntrada->obterDadosMovimento();
  Serial.printf("Status: %s | Cmd: %d | Vel: %d\n", 
                controleEntrada->estaConectado() ? "ON" : "OFF",
                movimento.comando, movimento.velocidade);
}

void handlePeriodicUpdates() {
  unsigned long now = millis();
  
  if (now - lastStatusUpdate > 15000) {
    printSystemStatus();
    lastStatusUpdate = now;
  }
}

void updateStatusLED() {
  static unsigned long lastLedUpdate = 0;
  static bool ledState = false;
  unsigned long now = millis();
  
  ControleDabble* dabbleController = static_cast<ControleDabble*>(controleEntrada);
  
  if (dabbleController->estaConectado()) {
    digitalWrite(STATUS_LED_PIN, HIGH);
  } else if (dabbleController->bluetoothPronto()) {
    if (now - lastLedUpdate > 500) {
      ledState = !ledState;
      digitalWrite(STATUS_LED_PIN, ledState);
      lastLedUpdate = now;
    }
  } else {
    digitalWrite(STATUS_LED_PIN, LOW);
  }
}

void blinkErrorLED() {
  static unsigned long lastBlink = 0;
  static bool ledState = false;
  unsigned long now = millis();
  
  if (now - lastBlink > 200) {
    ledState = !ledState;
    digitalWrite(STATUS_LED_PIN, ledState);
    lastBlink = now;
  }
}

void setup() {
  Serial.begin(SERIAL_BAUDRATE);
  delay(1000);
  
  printWelcomeMessage();
  
  pinMode(STATUS_LED_PIN, OUTPUT);
  digitalWrite(STATUS_LED_PIN, LOW);
  
  Serial.println("Inicializando sistema...");
  if (!mecanumDrive.begin()) {
    Serial.println("Erro nos motores!");
    return;
  }
  
  controleEntrada = new ControleDabble();
  
  if (!controleEntrada->iniciar()) {
    Serial.println("Erro Bluetooth!");
    while (true) {
      blinkErrorLED();
      delay(100);
    }
  }
  
  systemInitialized = true;
  digitalWrite(STATUS_LED_PIN, HIGH);
  
  Serial.println("Sistema pronto!");
  printControlInstructions();
}

void loop() {
  if (!systemInitialized) {
    blinkErrorLED();
    delay(1000);
    return;
  }
  
  controleEntrada->atualizar();
  
  DadosMovimento movimento = controleEntrada->obterDadosMovimento();
  
  mecanumDrive.executeMovement(movimento);
  
  mecanumDrive.checkTimeout();
  
  handlePeriodicUpdates();
  
  updateStatusLED();
  
  delay(10);
}
