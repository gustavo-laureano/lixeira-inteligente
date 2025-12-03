/*
Exemplo de código Arduino para receber comandos da Lixeira Inteligente
e controlar motores para movimento.

Comando recebido: OBJETO:POSICAO:DISTANCIA
Exemplos:
  - BOTTLE:LEFT:FAR        → Garrafa longe à esquerda (avançar rápido)
  - CAN:CENTER:MEDIUM      → Lata média distância no centro (avançar devagar)
  - CUP:RIGHT:CLOSE        → Copo perto à direita (ajustar posição)
  - BOWL:CENTER:VERY_CLOSE → Tigela muito perto (RECUAR)
*/

// Pinos dos Motores (ajuste conforme seu hardware)
const int MOTOR_LEFT_PIN1 = 2;
const int MOTOR_LEFT_PIN2 = 3;
const int MOTOR_RIGHT_PIN1 = 4;
const int MOTOR_RIGHT_PIN2 = 5;
const int MOTOR_ENABLE_LEFT = 9;   // PWM
const int MOTOR_ENABLE_RIGHT = 10; // PWM

// Velocidade dos motores (0-255)
const int SPEED_FAST = 200;      // Velocidade rápida (objeto longe)
const int SPEED_NORMAL = 150;    // Velocidade normal
const int SPEED_SLOW = 100;      // Velocidade lenta (objeto perto)
const int SPEED_TURN = 120;      // Velocidade de curva

// Tempo de movimento (ms)
const int MOVE_TIME_FAST = 800;   // Tempo avançar rápido
const int MOVE_TIME_NORMAL = 500; // Tempo avançar normal
const int MOVE_TIME_SLOW = 300;   // Tempo avançar devagar
const int TURN_TIME = 300;        // Tempo de curva

void setup() {
  // Inicializa comunicação serial
  Serial.begin(9600);
  Serial.println("Arduino: Lixeira Inteligente - Pronto!");
  
  // Configura pinos dos motores
  pinMode(MOTOR_LEFT_PIN1, OUTPUT);
  pinMode(MOTOR_LEFT_PIN2, OUTPUT);
  pinMode(MOTOR_RIGHT_PIN1, OUTPUT);
  pinMode(MOTOR_RIGHT_PIN2, OUTPUT);
  pinMode(MOTOR_ENABLE_LEFT, OUTPUT);
  pinMode(MOTOR_ENABLE_RIGHT, OUTPUT);
  
  // Para os motores
  stopMotors();
}

void loop() {
  // Verifica se há dados na serial
  if (Serial.available() > 0) {
    String command = Serial.readStringUntil('\n');
    command.trim();
    
    if (command.length() > 0) {
      Serial.print("Recebido: ");
      Serial.println(command);
      
      processCommand(command);
      
      // Envia confirmação
      Serial.println("OK");
    }
  }
}

void processCommand(String cmd) {
  // Parse: OBJETO:POSICAO:DISTANCIA
  int firstColon = cmd.indexOf(':');
  int secondColon = cmd.indexOf(':', firstColon + 1);
  
  if (firstColon == -1 || secondColon == -1) {
    Serial.println("Erro: Formato inválido");
    return;
  }
  
  String object = cmd.substring(0, firstColon);
  String position = cmd.substring(firstColon + 1, secondColon);
  String distance = cmd.substring(secondColon + 1);
  
  Serial.print("Objeto: ");
  Serial.print(object);
  Serial.print(" | Posição: ");
  Serial.print(position);
  Serial.print(" | Distância: ");
  Serial.println(distance);
  
  // ========================================
  // LÓGICA BASEADA NA DISTÂNCIA
  // ========================================
  
  if (distance == "VERY_CLOSE") {
    // ⬅️ MUITO PERTO - RECUAR!
    Serial.println("Ação: RECUAR - Objeto muito perto!");
    moveBackward(MOVE_TIME_NORMAL);
    delay(200);
    
  } else if (distance == "CLOSE") {
    // ⏸️ PERTO - PARAR (já alcançou o objeto)
    Serial.println("Ação: PARAR - Objeto alcançado!");
    stopMotors();
    delay(1000);
    
  } else if (distance == "MEDIUM") {
    // 🐢 DISTÂNCIA MÉDIA - Aproximar DEVAGAR
    Serial.println("Ação: Aproximar DEVAGAR");
    
    if (position == "LEFT") {
      turnLeft();
      delay(100);
      moveForward(MOVE_TIME_SLOW, SPEED_SLOW);
    } 
    else if (position == "RIGHT") {
      turnRight();
      delay(100);
      moveForward(MOVE_TIME_SLOW, SPEED_SLOW);
    } 
    else if (position == "CENTER") {
      moveForward(MOVE_TIME_SLOW, SPEED_SLOW);
    }
    
  } else if (distance == "FAR") {
    // 🚀 LONGE - Avançar RÁPIDO
    Serial.println("Ação: Avançar RÁPIDO");
    
    if (position == "LEFT") {
      turnLeft();
      delay(100);
      moveForward(MOVE_TIME_FAST, SPEED_FAST);
    } 
    else if (position == "RIGHT") {
      turnRight();
      delay(100);
      moveForward(MOVE_TIME_FAST, SPEED_FAST);
    } 
    else if (position == "CENTER") {
      moveForward(MOVE_TIME_FAST, SPEED_FAST);
    }
    
  } else {
    Serial.println("Distância desconhecida!");
  }
  
  // Para após movimento
  delay(200);
  stopMotors();
}

// Funções de movimento dos motores

void moveForward(int duration, int speed) {
  Serial.print("Ação: Mover para frente (vel: ");
  Serial.print(speed);
  Serial.println(")");
  
  digitalWrite(MOTOR_LEFT_PIN1, HIGH);
  digitalWrite(MOTOR_LEFT_PIN2, LOW);
  digitalWrite(MOTOR_RIGHT_PIN1, HIGH);
  digitalWrite(MOTOR_RIGHT_PIN2, LOW);
  
  analogWrite(MOTOR_ENABLE_LEFT, speed);
  analogWrite(MOTOR_ENABLE_RIGHT, speed);
  
  delay(duration);
}

void moveBackward(int duration) {
  Serial.println("Ação: Mover para TRÁS");
  
  digitalWrite(MOTOR_LEFT_PIN1, LOW);
  digitalWrite(MOTOR_LEFT_PIN2, HIGH);
  digitalWrite(MOTOR_RIGHT_PIN1, LOW);
  digitalWrite(MOTOR_RIGHT_PIN2, HIGH);
  
  analogWrite(MOTOR_ENABLE_LEFT, SPEED_NORMAL);
  analogWrite(MOTOR_ENABLE_RIGHT, SPEED_NORMAL);
  
  delay(duration);
}

void turnLeft() {
  Serial.println("Ação: Virar à esquerda");
  
  digitalWrite(MOTOR_LEFT_PIN1, LOW);
  digitalWrite(MOTOR_LEFT_PIN2, HIGH);
  digitalWrite(MOTOR_RIGHT_PIN1, HIGH);
  digitalWrite(MOTOR_RIGHT_PIN2, LOW);
  
  analogWrite(MOTOR_ENABLE_LEFT, SPEED_TURN);
  analogWrite(MOTOR_ENABLE_RIGHT, SPEED_TURN);
  
  delay(TURN_TIME);
}

void turnRight() {
  Serial.println("Ação: Virar à direita");
  
  digitalWrite(MOTOR_LEFT_PIN1, HIGH);
  digitalWrite(MOTOR_LEFT_PIN2, LOW);
  digitalWrite(MOTOR_RIGHT_PIN1, LOW);
  digitalWrite(MOTOR_RIGHT_PIN2, HIGH);
  
  analogWrite(MOTOR_ENABLE_LEFT, SPEED_TURN);
  analogWrite(MOTOR_ENABLE_RIGHT, SPEED_TURN);
  
  delay(TURN_TIME);
}

void stopMotors() {
  digitalWrite(MOTOR_LEFT_PIN1, LOW);
  digitalWrite(MOTOR_LEFT_PIN2, LOW);
  digitalWrite(MOTOR_RIGHT_PIN1, LOW);
  digitalWrite(MOTOR_RIGHT_PIN2, LOW);
  
  analogWrite(MOTOR_ENABLE_LEFT, 0);
  analogWrite(MOTOR_ENABLE_RIGHT, 0);
}
