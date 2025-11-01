// Carrinho Mecanum ESP32
// Controle via API WebSocket

#include <Arduino.h>
#include "Config.h"
#include "MecanumDrive.h"
#include "APIreceiver.h"

MecanumDrive mecanumDrive;
RobotReceiver robotReceiver;

unsigned long lastStatusUpdate = 0;
bool systemInitialized = false;

void printWelcomeMessage() {
  Serial.println("ESP32 Carrinho Mecanum - API Control");
  Serial.println("Aguardando comandos via WebSocket...");
}

void printControlInstructions() {
  Serial.println("Comandos aceitos via WebSocket:");
  Serial.println("- 'V:vy,vx' = Vetor de movimento continuo (vy:-1..1, vx:-1..1)");
}

void printSystemStatus() {
  Serial.printf("Sistema ativo | Motores: OK | WiFi: Conectado\n");
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
  
  if (now - lastLedUpdate > 1000) {
    ledState = !ledState;
    digitalWrite(STATUS_LED_PIN, ledState);
    lastLedUpdate = now;
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
  
  systemInitialized = true;
  digitalWrite(STATUS_LED_PIN, HIGH);
  
  Serial.println("Sistema pronto!");
  printControlInstructions();

  // Inicia o receptor WebSocket para comandos remotos (API)
  robotReceiver.begin(WIFI_SSID, WIFI_PASSWORD);
}

void loop() {
  if (!systemInitialized) {
    blinkErrorLED();
    delay(1000);
    return;
  }
  
  // Loop do receptor WebSocket (mantém conexão e processa mensagens)
  robotReceiver.loop();
  
  // Timeout de segurança dos motores
  mecanumDrive.checkTimeout();
  
  handlePeriodicUpdates();
  
  updateStatusLED();

  delay(10);
}

// Handler para o novo protocolo de vetor: V:vy,vx
void handleRobotVector(float vy, float vx) {
  // Garante limites -1.0 .. 1.0
  vy = constrain(vy, -1.0f, 1.0f);
  vx = constrain(vx, -1.0f, 1.0f);

  // Se ambos zeros, para os motores
  if (fabs(vy) < 0.0001f && fabs(vx) < 0.0001f) {
    mecanumDrive.stopAllMotors();
    return;
  }

  // Encaminha para o controlador de cinemática inversa (sem rotação)
  mecanumDrive.executeVector(vy, vx);
}
