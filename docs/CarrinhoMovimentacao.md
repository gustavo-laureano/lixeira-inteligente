# 🤖 CarrinhoMovimentacao — Módulo de Movimentação (Mecanum)

Este documento contém a parte do repositório responsável pelo controle de movimentação do carrinho com rodas mecanum. O sistema suporta múltiplos modos de controle:

1. **APIreceiver (WebSocket)** - Controle via sistema de visão computacional ⭐
2. **Dabble (Bluetooth)** - Controle manual via app mobile
3. **Serial** - Controle via Monitor Serial (debug/teste)

## 📋 Arquivos Principais

- `include/Config.h` - Pinos e configurações PWM
- `include/MecanumDrive.h` - Implementação de controle das 4 rodas mecanum
- `include/APIreceiver.h` - Controle via WebSocket (sistema de visão)
- `include/ControleDabble.h` - Controle via Bluetooth (Dabble)
- `include/ControleSerial.h` - Controle via Serial (debug)
- `src/main.cpp` - Entrypoint que instancia o controlador

## 🌐 Controle via WebSocket (Sistema de Visão)

### Protocolo V:vy,vx

O sistema de visão computacional envia comandos no formato **V:vy,vx** onde:

- **V**: Identificador de comando de vetor
- **vy**: Velocidade normalizada [-1.0, 1.0] no eixo Y (frente/trás)
- **vx**: Velocidade normalizada [-1.0, 1.0] no eixo X (esquerda/direita)

### Exemplos de Comandos

```cpp
// Formato: V:vy,vx

"V:0.500,0.000"   // Frente (50% velocidade)
"V:-0.500,0.000"  // Trás (50% velocidade)
"V:0.000,0.500"   // Direita (50% velocidade)
"V:0.000,-0.500"  // Esquerda (50% velocidade)
"V:0.707,0.707"   // Diagonal frente-direita (70%)
"V:0.000,0.000"   // Parar
"V:1.000,0.000"   // Frente máxima velocidade
```

### Como Funciona

```cpp
// APIreceiver.h - handleMessage()

if (message.startsWith("V:") || message.startsWith("v:")) {
    // Parse: V:vy,vx
    int commaIndex = message.indexOf(',', 2);
    String sVy = message.substring(2, commaIndex);
    String sVx = message.substring(commaIndex + 1);
    
    float vy = sVy.toFloat();  // Frente/Trás
    float vx = sVx.toFloat();  // Esquerda/Direita
    
    // Chama handler no main.cpp
    handleRobotVector(vy, vx);
}
```

```cpp
// main.cpp - handleRobotVector()

void handleRobotVector(float vy, float vx) {
    // Constrain valores [-1, 1]
    vy = constrain(vy, -1.0f, 1.0f);
    vx = constrain(vx, -1.0f, 1.0f);
    
    // Deadzone (evita movimento com valores muito pequenos)
    if (fabs(vy) < 0.0001f && fabs(vx) < 0.0001f) {
        mecanumDrive.stopAllMotors();
        Serial.println("⏹️  STOP");
    } else {
        // Executar movimento omnidirecional
        mecanumDrive.executeVector(vy, vx);
        Serial.printf("🎯 Vector: vy=%.3f, vx=%.3f\n", vy, vx);
    }
}
```

### Configuração WebSocket

Edite `include/APIreceiver.h`:

```cpp
// Configuração do servidor WebSocket
const char* SERVER_HOST = "192.168.1.100";  // IP do PC com sistema de visão
const int SERVER_PORT = 8000;               // Porta do api_server.py
const char* SERVER_PATH = "/ws/robot";      // Endpoint WebSocket
```

Edite `include/Config.h`:

```cpp
// Configurações WiFi
#define WIFI_SSID "SUA_REDE_WIFI"
#define WIFI_PASSWORD "SUA_SENHA"
```

### Fluxo de Comunicação

```
┌─────────────────────────────────────────────────────────────────┐
│ 1. Sistema de Visão (Python)                                   │
│    └─> Detecta objeto → Calcula trajetória → Gera comando     │
│        robot.send_raw("V:0.500,0.300")                         │
└─────────────────────────────────────────────────────────────────┘
                               ↓ (WebSocket)
┌─────────────────────────────────────────────────────────────────┐
│ 2. API Server (api_server.py)                                  │
│    └─> Broker WebSocket: Repassa mensagem para ESP32          │
└─────────────────────────────────────────────────────────────────┘
                               ↓ (WebSocket)
┌─────────────────────────────────────────────────────────────────┐
│ 3. ESP32 (APIreceiver.h)                                       │
│    └─> Recebe "V:0.500,0.300"                                 │
│        Parse: vy=0.5, vx=0.3                                   │
│        handleRobotVector(0.5, 0.3)                             │
└─────────────────────────────────────────────────────────────────┘
                               ↓
┌─────────────────────────────────────────────────────────────────┐
│ 4. MecanumDrive.executeVector()                                │
│    └─> Calcula velocidades dos 4 motores                      │
│        Move o carrinho!                                         │
└─────────────────────────────────────────────────────────────────┘
```

## 🎮 Controle via Dabble (Bluetooth)

Ver seção anterior do documento para detalhes completos sobre controle Dabble.
