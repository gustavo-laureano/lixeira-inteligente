# 📡 API - Sistema de Comunicação WebSocket/UDP

Este diretório contém os componentes backend do sistema de teste de latência para controle de robô via rede.

## 📁 Estrutura

```
api/
├── api_server.py          # Servidor broker WebSocket (TCP)
├── api_receiver.py        # Cliente receptor para Raspberry Pi (TCP)
├── api_server_udp.py      # Servidor broker UDP (opcional)
├── api_receiver_udp.py    # Cliente receptor UDP para Raspberry Pi (opcional)
└── README.md              # Este arquivo
```

## 🚀 Uso Rápido

### Servidor WebSocket (PC/Servidor)

```bash
cd api
python api_server.py
```

O servidor estará disponível em:
- **WebSocket Controller**: `ws://0.0.0.0:8000/ws/controller`
- **WebSocket Robot**: `ws://0.0.0.0:8000/ws/robot`
- **Health Check**: `http://0.0.0.0:8000/health`

### Receptor WebSocket (Raspberry Pi)

1. Edite `api_receiver.py` e configure:
   - `SERVER_URI`: IP do servidor (ex: `ws://192.168.1.100:8000/ws/robot`)
   - `SERIAL_PORT`: Porta serial do Arduino (ex: `/dev/ttyUSB0`)
   - `BAUDRATE`: Velocidade serial (ex: `115200`)

2. Execute:
```bash
cd api
python api_receiver.py
```

## 📋 Requisitos

```bash
pip install fastapi uvicorn[standard] websockets pyserial
```

Ou instale todas as dependências do projeto:
```bash
pip install -r ../requirements.txt
```

## 🔄 Protocolo

O sistema usa comandos de caractere único definidos em `include/ControleSerial.h`:

- **Movimento**: `w` (frente), `s` (trás), `a` (esquerda), `d` (direita)
- **Rotação**: `q` (girar esquerda), `e` (girar direita)
- **Parada**: `x`

## 🧪 Teste de Latência

O servidor responde a mensagens `"ping"` com `"pong"` para medir Round-Trip Time (RTT).

## 📊 Comparação TCP vs UDP

- **WebSocket (TCP)**: Confiável, garantia de entrega, latência ~5-50ms
- **UDP**: Mais rápido, ~1-5ms, mas sem garantia de entrega

Use os arquivos `*_udp.py` para testar latência com UDP.

