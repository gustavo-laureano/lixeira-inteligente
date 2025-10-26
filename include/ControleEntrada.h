#ifndef CONTROLE_ENTRADA_H
#define CONTROLE_ENTRADA_H

enum ComandoMovimento {
  PARAR = 0, MOVER_FRENTE, MOVER_TRAS, MOVER_ESQUERDA, MOVER_DIREITA,
  GIRAR_ESQUERDA, GIRAR_DIREITA, MOVER_FRENTE_ESQUERDA, MOVER_FRENTE_DIREITA,
  MOVER_TRAS_ESQUERDA, MOVER_TRAS_DIREITA
};

struct DadosMovimento {
  ComandoMovimento comando;
  int velocidade;
  bool ativo;
  unsigned long timestamp;
};

class ControleEntrada {
public:
  virtual ~ControleEntrada() = default;
  virtual bool iniciar() = 0;
  virtual void atualizar() = 0;
  virtual DadosMovimento obterDadosMovimento() = 0;
  virtual bool estaConectado() = 0;
  virtual String obterNomeControlador() = 0;
  virtual void aoConectar() { }
  virtual void aoDesconectar() { }
  virtual void resetar() { }
};

class ControleEntradaBase : public ControleEntrada {
protected:
  DadosMovimento movimentoAtual;
  bool conectado;
  unsigned long ultimaAtualizacao;
  String nomeControlador;
  
public:
  ControleEntradaBase(const String& nome) 
    : conectado(false), ultimaAtualizacao(0), nomeControlador(nome) {
    movimentoAtual = {PARAR, 0, false, 0};
  }
  
  virtual bool estaConectado() override { return conectado; }
  virtual String obterNomeControlador() override { return nomeControlador; }
  virtual DadosMovimento obterDadosMovimento() override { return movimentoAtual; }
  
protected:
  void definirDadosMovimento(ComandoMovimento cmd, int velocidade = 150) {
    movimentoAtual.comando = cmd;
    movimentoAtual.velocidade = constrain(velocidade, 0, 255);
    movimentoAtual.ativo = (cmd != PARAR);
    movimentoAtual.timestamp = millis();
  }
  
  bool comandoExpirou(unsigned long timeout = 500) {
    return (millis() - movimentoAtual.timestamp) > timeout;
  }
};

#endif