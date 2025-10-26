#ifndef MECANUM_DRIVE_H
#define MECANUM_DRIVE_H

#include <Arduino.h>
#include "Config.h"
#include "ControleEntrada.h"

struct Motor {
  int pwmPin, dir1Pin, dir2Pin, pwmChannel, currentSpeed;
  bool reversed;
  
  Motor(int pwm, int d1, int d2, int channel, bool rev = false) 
    : pwmPin(pwm), dir1Pin(d1), dir2Pin(d2), pwmChannel(channel), 
      currentSpeed(0), reversed(rev) {}
};

class MecanumDrive {
private:
  Motor motorA, motorC, motorB, motorD;
  bool initialized;
  unsigned long lastCommandTime;
  ComandoMovimento lastCommand;
  
public:
  MecanumDrive() 
    : motorA(MOTOR_A_PWM_PIN, MOTOR_A_DIR1_PIN, MOTOR_A_DIR2_PIN, 0),
      motorC(MOTOR_C_PWM_PIN, MOTOR_C_DIR1_PIN, MOTOR_C_DIR2_PIN, 1),
      motorB(MOTOR_B_PWM_PIN, MOTOR_B_DIR1_PIN, MOTOR_B_DIR2_PIN, 2),
      motorD(MOTOR_D_PWM_PIN, MOTOR_D_DIR1_PIN, MOTOR_D_DIR2_PIN, 3),
      initialized(false), lastCommandTime(0), lastCommand(PARAR) {}
  
  // Inicialização
  bool begin() {
    Serial.println("Inicializando motores...");
    
    // Configura pinos dos motores
    setupMotor(motorA);
    setupMotor(motorC);
    setupMotor(motorB);
    setupMotor(motorD);
    
    // Para todos os motores
    stopAllMotors();
    
    initialized = true;
    Serial.println("Motores OK!");
    
    return true;
  }
  
  // Executa comando de movimento
  void executeMovement(const DadosMovimento& data) {
    if (!initialized) return;
    
    lastCommandTime = millis();
    
    // Executa o movimento baseado no comando
    switch (data.comando) {
      case MOVER_FRENTE: moveForward(data.velocidade); break;
      case MOVER_TRAS: moveBackward(data.velocidade); break;
      case MOVER_ESQUERDA: moveLeft(data.velocidade); break;
      case MOVER_DIREITA: moveRight(data.velocidade); break;
      case GIRAR_ESQUERDA: rotateLeft(data.velocidade); break;
      case GIRAR_DIREITA: rotateRight(data.velocidade); break;
      case MOVER_FRENTE_ESQUERDA: moveForwardLeft(data.velocidade); break;
      case MOVER_FRENTE_DIREITA: moveForwardRight(data.velocidade); break;
      case MOVER_TRAS_ESQUERDA: moveBackwardLeft(data.velocidade); break;
      case MOVER_TRAS_DIREITA: moveBackwardRight(data.velocidade); break;
      case PARAR:
      default: stopAllMotors(); break;
    }
  }
  
  // Para todos os motores
  void stopAllMotors() {
    setMotorSpeed(motorA, 0);
    setMotorSpeed(motorC, 0);
    setMotorSpeed(motorB, 0);
    setMotorSpeed(motorD, 0);
  }
  
  // Verifica timeout de comandos
  void checkTimeout(unsigned long timeout = COMMAND_TIMEOUT) {
    if (initialized && (millis() - lastCommandTime) > timeout) {
      if (lastCommand != PARAR) {
        stopAllMotors();
        lastCommand = PARAR;
      }
    }
  }
  
  // Status dos motores
  void printStatus() {
    Serial.printf("Motores A:%d C:%d B:%d D:%d\n", 
                  motorA.currentSpeed, motorC.currentSpeed,
                  motorB.currentSpeed, motorD.currentSpeed);
  }

private:
  // Configura um motor
  void setupMotor(Motor& motor) {
    pinMode(motor.dir1Pin, OUTPUT);
    pinMode(motor.dir2Pin, OUTPUT);
    pinMode(motor.pwmPin, OUTPUT);
    
    // Configura PWM
    ledcSetup(motor.pwmChannel, PWM_FREQUENCY, PWM_RESOLUTION);
    ledcAttachPin(motor.pwmPin, motor.pwmChannel);
    
    // Estado inicial parado
    digitalWrite(motor.dir1Pin, LOW);
    digitalWrite(motor.dir2Pin, LOW);
    ledcWrite(motor.pwmChannel, 0);
    
    motor.currentSpeed = 0;
  }
  
  // Controla velocidade e direção de um motor
  void setMotorSpeed(Motor& motor, int speed) {
    speed = constrain(speed, -255, 255);
    motor.currentSpeed = speed;
    
    if (motor.reversed) speed = -speed;  // Inverte se necessário
    
    if (speed > 0) {
      // Frente
      digitalWrite(motor.dir1Pin, HIGH);
      digitalWrite(motor.dir2Pin, LOW);
      ledcWrite(motor.pwmChannel, abs(speed));
    } else if (speed < 0) {
      // Trás
      digitalWrite(motor.dir1Pin, LOW);
      digitalWrite(motor.dir2Pin, HIGH);
      ledcWrite(motor.pwmChannel, abs(speed));
    } else {
      // Parado
      digitalWrite(motor.dir1Pin, LOW);
      digitalWrite(motor.dir2Pin, LOW);
      ledcWrite(motor.pwmChannel, 0);
    }
  }
  
  // Movimentos específicos para rodas mecanum
  void moveForward(int speed) {
    setMotorSpeed(motorA, speed);    // Frontal Esquerdo
    setMotorSpeed(motorC, speed);    // Frontal Direito
    setMotorSpeed(motorB, speed);    // Traseiro Esquerdo
    setMotorSpeed(motorD, speed);    // Traseiro Direito
  }
  
  void moveBackward(int speed) {
    setMotorSpeed(motorA, -speed);
    setMotorSpeed(motorC, -speed);
    setMotorSpeed(motorB, -speed);
    setMotorSpeed(motorD, -speed);
  }
  
  void moveLeft(int speed) {
    setMotorSpeed(motorA, -speed);   // A: para trás
    setMotorSpeed(motorC, speed);    // C: para frente
    setMotorSpeed(motorB, speed);    // B: para frente
    setMotorSpeed(motorD, -speed);   // D: para trás
  }
  
  void moveRight(int speed) {
    setMotorSpeed(motorA, speed);    // A: para frente
    setMotorSpeed(motorC, -speed);   // C: para trás
    setMotorSpeed(motorB, -speed);   // B: para trás
    setMotorSpeed(motorD, speed);    // D: para frente
  }
  
  void rotateLeft(int speed) {
    setMotorSpeed(motorA, -speed);
    setMotorSpeed(motorC, speed);
    setMotorSpeed(motorB, -speed);
    setMotorSpeed(motorD, speed);
  }
  
  void rotateRight(int speed) {
    setMotorSpeed(motorA, speed);
    setMotorSpeed(motorC, -speed);
    setMotorSpeed(motorB, speed);
    setMotorSpeed(motorD, -speed);
  }
  
  void moveForwardLeft(int speed) {
    setMotorSpeed(motorA, 0);        // A: parado
    setMotorSpeed(motorC, speed);    // C: para frente
    setMotorSpeed(motorB, speed);    // B: para frente
    setMotorSpeed(motorD, 0);        // D: parado
  }
  
  void moveForwardRight(int speed) {
    setMotorSpeed(motorA, speed);    // A: para frente
    setMotorSpeed(motorC, 0);        // C: parado
    setMotorSpeed(motorB, 0);        // B: parado
    setMotorSpeed(motorD, speed);    // D: para frente
  }
  
  void moveBackwardLeft(int speed) {
    setMotorSpeed(motorA, -speed);   // A: para trás
    setMotorSpeed(motorC, 0);        // C: parado
    setMotorSpeed(motorB, 0);        // B: parado
    setMotorSpeed(motorD, -speed);   // D: para trás
  }
  
  void moveBackwardRight(int speed) {
    setMotorSpeed(motorA, 0);        // A: parado
    setMotorSpeed(motorC, -speed);   // C: para trás
    setMotorSpeed(motorB, -speed);   // B: para trás
    setMotorSpeed(motorD, 0);        // D: parado
  }
};

#endif // MECANUM_DRIVE_H