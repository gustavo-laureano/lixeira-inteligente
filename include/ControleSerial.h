// ===== EXEMPLO: CONTROLADOR SERIAL =====
// Este arquivo demonstra como criar um novo tipo de controle
// Para usar, inclua este arquivo e substitua ControleDabble
// por ControleSerial no main.cpp

#ifndef CONTROLE_SERIAL_H
#define CONTROLE_SERIAL_H

#include "ControleEntrada.h"
#include "Config.h"

class ControleSerial : public ControleEntradaBase {
private:
  String bufferEntrada;
  int velocidadeAtual;
  
public:
  ControleSerial() 
    : ControleEntradaBase("Terminal Serial"), 
      velocidadeAtual(DEFAULT_SPEED) {}
  
  virtual bool iniciar() override {
    Serial.println("⌨️ Controlador Serial ativo!");
    Serial.println("=== MOVIMENTOS ===");
    Serial.println("w(frente) s(trás) a(esquerda) d(direita)");
    Serial.println("q(girar esq) e(girar dir) x(parar)");
    Serial.println("=== DIAGONAIS ===");
    Serial.println("r(frente-direita) t(frente-esquerda)");
    Serial.println("f(trás-direita) g(trás-esquerda)");
    Serial.println("=== VELOCIDADES ===");
    Serial.println("1(devagar) 2(normal) 3(rápido) 4(muito rápido)");
    Serial.println("+(velocidade+) -(velocidade-)");
    conectado = true;
    return true;
  }
  
  virtual void atualizar() override {
    if (Serial.available()) {
      char entrada = Serial.read();
      processarComandoSerial(entrada);
    }
    
    // Auto-stop após timeout
    if (comandoExpirou(1000)) {
      definirDadosMovimento(PARAR, 0);
    }
  }
  
private:
  void processarComandoSerial(char cmd) {
    ComandoMovimento movimento = PARAR;
    
    switch (cmd) {
      // Movimentos básicos
      case 'w': case 'W': movimento = MOVER_FRENTE; break;
      case 's': case 'S': movimento = MOVER_TRAS; break;
      case 'a': case 'A': movimento = MOVER_ESQUERDA; break;
      case 'd': case 'D': movimento = MOVER_DIREITA; break;
      case 'q': case 'Q': movimento = GIRAR_ESQUERDA; break;
      case 'e': case 'E': movimento = GIRAR_DIREITA; break;
      case 'x': case 'X': movimento = PARAR; break;
      
      // Movimentos diagonais
      case 'r': case 'R': movimento = MOVER_FRENTE_DIREITA; break;   // Frente-Direita
      case 't': case 'T': movimento = MOVER_FRENTE_ESQUERDA; break;    // Frente-Esquerda  
      case 'f': case 'F': movimento = MOVER_TRAS_DIREITA; break;  // Trás-Direita
      case 'g': case 'G': movimento = MOVER_TRAS_ESQUERDA; break;   // Trás-Esquerda
      
      // Velocidades predefinidas
      case '1': velocidadeAtual = 80; Serial.println("🐢 Velocidade: DEVAGAR (80)"); return;
      case '2': velocidadeAtual = 140; Serial.println("🚶 Velocidade: NORMAL (140)"); return;
      case '3': velocidadeAtual = 180; Serial.println("🏃 Velocidade: RÁPIDO (180)"); return;
      case '4': velocidadeAtual = 200; Serial.println("🚀 Velocidade: MUITO RÁPIDO (200)"); return;
      
      // Ajuste manual de velocidade
      case '+': 
        velocidadeAtual = min(200, velocidadeAtual + 20); 
        Serial.printf("⬆️ Velocidade: %d\n", velocidadeAtual);
        return;
      case '-': 
        velocidadeAtual = max(50, velocidadeAtual - 20); 
        Serial.printf("⬇️ Velocidade: %d\n", velocidadeAtual);
        return;
        
      default: return;
    }
    
    definirDadosMovimento(movimento, velocidadeAtual);
    imprimirInfoMovimento(cmd, movimento);
  }
  
  void imprimirInfoMovimento(char cmd, ComandoMovimento movimento) {
    String direcao = "";
    switch (movimento) {
      case MOVER_FRENTE: direcao = "⬆️ FRENTE"; break;
      case MOVER_TRAS: direcao = "⬇️ TRÁS"; break;
      case MOVER_ESQUERDA: direcao = "⬅️ ESQUERDA"; break;
      case MOVER_DIREITA: direcao = "➡️ DIREITA"; break;
      case MOVER_FRENTE_ESQUERDA: direcao = "↖️ FRENTE-ESQUERDA"; break;
      case MOVER_FRENTE_DIREITA: direcao = "↗️ FRENTE-DIREITA"; break;
      case MOVER_TRAS_ESQUERDA: direcao = "↙️ TRÁS-ESQUERDA"; break;
      case MOVER_TRAS_DIREITA: direcao = "↘️ TRÁS-DIREITA"; break;
      case GIRAR_ESQUERDA: direcao = "🔄 GIRAR ESQUERDA"; break;
      case GIRAR_DIREITA: direcao = "🔃 GIRAR DIREITA"; break;
      case PARAR: direcao = "⏹️ PARAR"; break;
    }
    Serial.printf("Comando: %c | %s | Vel: %d\n", cmd, direcao.c_str(), velocidadeAtual);
  }
};

// ===== EXEMPLO: CONTROLADOR WIFI =====
// Exemplo de como criar controle via rede WiFi

/*
#include <WiFi.h>
#include <WebServer.h>

class ControleWiFi : public ControleEntradaBase {
private:
  WebServer server;
  
public:
  ControleWiFi() : ControleEntradaBase("WiFi Web"), server(80) {}
  
  virtual bool iniciar() override {
    WiFi.begin("SUA_REDE", "SUA_SENHA");
    // Configurar server web...
    return true;
  }
  
  virtual void atualizar() override {
    server.handleClient();
    // Processar comandos HTTP...
  }
};
*/

// ===== EXEMPLO: CONTROLADOR JOYSTICK =====
// Exemplo para joystick analógico

/*
class ControleJoystick : public ControleEntradaBase {
private:
  int pinoX, pinoY;
  
public:
  ControleJoystick(int x, int y) 
    : ControleEntradaBase("Joystick Analógico"), pinoX(x), pinoY(y) {}
  
  virtual bool iniciar() override {
    pinMode(pinoX, INPUT);
    pinMode(pinoY, INPUT);
    conectado = true;
    return true;
  }
  
  virtual void atualizar() override {
    int x = analogRead(pinoX);
    int y = analogRead(pinoY);
    
    // Converter valores analógicos para comandos de movimento
    // Implementar deadzone, mapeamento, etc.
  }
};
*/

#endif // CONTROLE_SERIAL_H