#ifndef CONTROLE_DABBLE_H
#define CONTROLE_DABBLE_H

#include "ControleEntrada.h"
#include "Config.h"

// Configurações para a biblioteca Dabble
#define CUSTOM_SETTINGS
#define INCLUDE_GAMEPAD_MODULE

// Include da biblioteca após as definições
#include <DabbleESP32.h>

class ControleDabble : public ControleEntradaBase {
private:
  unsigned long ultimaVerificacaoConexao;
  bool dabbleInicializado;
  int velocidadeAtual;
  bool usarJoystick;
  
public:
  ControleDabble() 
    : ControleEntradaBase("Controle Dabble"), 
      ultimaVerificacaoConexao(0), 
      dabbleInicializado(false),
      velocidadeAtual(DEFAULT_SPEED),
      usarJoystick(false) {}
  
  virtual bool iniciar() override {
    Serial.println("Iniciando Bluetooth...");
    
    try {
      Dabble.begin(BT_DEVICE_NAME);
      dabbleInicializado = true;
      conectado = false;
      Serial.println("Bluetooth OK!");
      return true;
    } catch (...) {
      Serial.println("Erro Bluetooth!");
      return false;
    }
  }
  
  virtual void atualizar() override {
    if (!dabbleInicializado) return;
    
    Dabble.processInput();
    verificarStatusConexao();
    
    // Verifica modo de controle
    if (GamePad.isSelectPressed()) {
      usarJoystick = !usarJoystick;
      delay(200); // Debounce
      Serial.printf("Modo: %s\n", usarJoystick ? "Joystick" : "GamePad");
    }
    
    if (usarJoystick) {
      processarComandosJoystick();
    } else {
      processarComandosGamePad();
    }
    
    if (comandoExpirou()) {
      if (movimentoAtual.ativo) {
        definirDadosMovimento(PARAR, 0);
      }
    }
    
    ultimaAtualizacao = millis();
  }
  
  virtual void resetar() override {
    definirDadosMovimento(PARAR, 0);
    velocidadeAtual = DEFAULT_SPEED;
  }
  
  // Métodos específicos do Dabble
  void definirVelocidade(int velocidade) {
    velocidadeAtual = constrain(velocidade, MIN_SPEED, MAX_SPEED);
  }
  
  int obterVelocidade() const {
    return velocidadeAtual;
  }
  
  // Verifica se o Bluetooth está ativo e aguardando conexões
  bool bluetoothPronto() const {
    return dabbleInicializado;
  }
  
  // Verifica se há atividade recente (comandos recebidos)
  bool temAtividadeRecente() const {
    return (millis() - movimentoAtual.timestamp) < 1000;  // Atividade nos últimos 1s
  }

private:
  void verificarStatusConexao() {
    unsigned long agora = millis();
    if (agora - ultimaVerificacaoConexao > 1000) {
      bool estavConectado = conectado;
      bool temAtividade = temAtividadeRecente() || (agora - movimentoAtual.timestamp) < 3000;
      conectado = temAtividade && dabbleInicializado;
      
      if (conectado && !estavConectado) {
        aoConectar();
      } else if (!conectado && estavConectado) {
        aoDesconectar();
      }
      
      ultimaVerificacaoConexao = agora;
    }
  }
  
  void processarComandosGamePad() {
    ComandoMovimento novoComando = PARAR;
    bool comandoAtivo = false;
    
    if (GamePad.isUpPressed()) {
      if (GamePad.isLeftPressed()) {
        novoComando = MOVER_FRENTE_ESQUERDA;
      } else if (GamePad.isRightPressed()) {
        novoComando = MOVER_FRENTE_DIREITA;
      } else {
        novoComando = MOVER_FRENTE;
      }
      comandoAtivo = true;
    }
    else if (GamePad.isDownPressed()) {
      if (GamePad.isLeftPressed()) {
        novoComando = MOVER_TRAS_ESQUERDA;
      } else if (GamePad.isRightPressed()) {
        novoComando = MOVER_TRAS_DIREITA;
      } else {
        novoComando = MOVER_TRAS;
      }
      comandoAtivo = true;
    }
    else if (GamePad.isLeftPressed()) {
      novoComando = MOVER_ESQUERDA;
      comandoAtivo = true;
    }
    else if (GamePad.isRightPressed()) {
      novoComando = MOVER_DIREITA;
      comandoAtivo = true;
    }
    
    if (GamePad.isSquarePressed()) {
      novoComando = GIRAR_ESQUERDA;
      comandoAtivo = true;
    }
    else if (GamePad.isCirclePressed()) {
      novoComando = GIRAR_DIREITA;
      comandoAtivo = true;
    }
    
    if (GamePad.isTrianglePressed()) {
      ajustarVelocidade(25);
    }
    else if (GamePad.isCrossPressed()) {
      ajustarVelocidade(-25);
    }
    
    if (comandoAtivo || (!comandoAtivo && movimentoAtual.ativo)) {
      definirDadosMovimento(novoComando, velocidadeAtual);
    }
  }
  
  void processarComandosJoystick() {
    float x = GamePad.getXaxisData();
    float y = GamePad.getYaxisData();
    
    // Deadzone
    if (abs(x) < 20 && abs(y) < 20) {
      definirDadosMovimento(PARAR, 0);
      return;
    }
    
    ComandoMovimento novoComando = PARAR;
    int velocidade = map(sqrt(x*x + y*y), 0, 100, MIN_SPEED, velocidadeAtual);
    
    // Determina direção baseada no ângulo
    float angulo = atan2(y, x) * 180.0 / PI;
    if (angulo < 0) angulo += 360;
    
    if (angulo >= 315 || angulo < 45) {
      novoComando = MOVER_DIREITA;
    } else if (angulo >= 45 && angulo < 135) {
      novoComando = MOVER_FRENTE;
    } else if (angulo >= 135 && angulo < 225) {
      novoComando = MOVER_ESQUERDA;
    } else if (angulo >= 225 && angulo < 315) {
      novoComando = MOVER_TRAS;
    }
    
    // Movimentos diagonais
    if ((angulo >= 22.5 && angulo < 67.5)) {
      novoComando = MOVER_FRENTE_DIREITA;
    } else if ((angulo >= 112.5 && angulo < 157.5)) {
      novoComando = MOVER_FRENTE_ESQUERDA;
    } else if ((angulo >= 202.5 && angulo < 247.5)) {
      novoComando = MOVER_TRAS_ESQUERDA;
    } else if ((angulo >= 292.5 && angulo < 337.5)) {
      novoComando = MOVER_TRAS_DIREITA;
    }
    
    definirDadosMovimento(novoComando, velocidade);
  }
  
  void ajustarVelocidade(int delta) {
    static unsigned long ultimaMudancaVelocidade = 0;
    unsigned long agora = millis();
    
    if (agora - ultimaMudancaVelocidade > 200) {  // Evita mudanças muito rápidas
      definirVelocidade(velocidadeAtual + delta);
      ultimaMudancaVelocidade = agora;
    }
  }
  
  virtual void aoConectar() override {
    Serial.println("App conectado!");
    conectado = true;
  }
  
  virtual void aoDesconectar() override {
    Serial.println("App desconectado!");
    definirDadosMovimento(PARAR, 0);
    conectado = false;
  }
};

#endif // CONTROLE_DABBLE_H