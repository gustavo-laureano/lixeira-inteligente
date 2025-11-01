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
  Serial.println("- 'w' = Frente");
  Serial.println("- 's' = Tras");
  Serial.println("- 'a' = Esquerda");
  Serial.println("- 'd' = Direita");
  Serial.println("- 'q' = Girar Esquerda");
  Serial.println("- 'e' = Girar Direita");
  Serial.println("- 'x' = Parar");
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

// Implementação da função que será chamada pelo APIreceiver.h
// Converte um comando simples (um caracter) em um DadosMovimento
void handleRobotCommand(String command) {
  if (command.length() == 0) return;
  char c = command.charAt(0);
  // Normaliza para minúscula
  if (c >= 'A' && c <= 'Z') c = c + 32;

  DadosMovimento dm;
  dm.velocidade = DEFAULT_SPEED;
  dm.ativo = true;
  dm.timestamp = millis();

  switch (c) {
    case 'w': dm.comando = MOVER_FRENTE; break;    // frente
    case 's': dm.comando = MOVER_TRAS; break;      // trás
    case 'a': dm.comando = MOVER_ESQUERDA; break;  // esquerda
    case 'd': dm.comando = MOVER_DIREITA; break;   // direita
    case 'q': dm.comando = GIRAR_ESQUERDA; break;  // girar esquerda
    case 'e': dm.comando = GIRAR_DIREITA; break;   // girar direita
    case 'x': dm.comando = PARAR; dm.ativo = false; break; // parar
    default:
      // Comando desconhecido: ignora
      return;
  }

  // Executa o movimento imediatamente
  mecanumDrive.executeMovement(dm);
}
