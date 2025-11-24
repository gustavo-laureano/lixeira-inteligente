# 🚀 Quick Start Guide

Guia rápido para colocar a Lixeira Inteligente funcionando em 20 minutos!

## 📋 Pré-requisitos

- **PC Windows/Linux/Mac** (Python 3.11+)
- **Câmera USB** compatível (testado com webcams comuns)
- **ESP32** com WiFi para controle do robô
- **4 Rodas Mecanum** + 2x TB6612FNG
- Conexão com internet (para baixar dependências)

## ⚡ Instalação Rápida

### 1. Clonar o Repositório (1 min)

```bash
git clone https://github.com/gustavo-laureano/lixeira-inteligente.git
cd lixeira-inteligente
```

### 2. Instalar Python e Dependências (5 min)

**Windows:**
```powershell
# Instalar Python 3.11 (recomendado)
# Download: https://www.python.org/downloads/

# Criar ambiente virtual
python -m venv venv
venv\Scripts\activate

# Instalar dependências
pip install -r requirements.txt
```

**Linux/Mac:**
```bash
# Criar ambiente virtual
python3.11 -m venv venv
source venv/bin/activate

# Instalar dependências
pip install -r requirements.txt
```

### 3. Identificar Câmera (1 min)

```bash
# Windows/Linux/Mac
python detection/tools/camera_selector.py
# Anote o ID da câmera (geralmente 0 ou 1)
```

### 4. Configurar ESP32 (8 min)

#### 4.1 Instalar PlatformIO no VS Code

1. Instale [VS Code](https://code.visualstudio.com/)
2. Instale extensão **PlatformIO IDE**
3. Abra o projeto na pasta `lixeira-inteligente`

#### 4.2 Configurar WiFi e Servidor

Edite `include/APIreceiver.h`:

```cpp
// Ajuste estes valores conforme seu ambiente
const char* SERVER_HOST = "192.168.1.100";  // IP do seu PC
const int   SERVER_PORT = 8000;
const char* SERVER_PATH = "/ws/robot";
```

Edite `include/Config.h`:

```cpp
// Configurações WiFi
#define WIFI_SSID           "SUA_REDE_WIFI"
#define WIFI_PASSWORD       "SUA_SENHA_WIFI"
```

#### 4.3 Upload para ESP32

1. Conecte ESP32 via USB
2. No PlatformIO: **Build** e **Upload**
3. Abra **Serial Monitor** (115200 baud)
4. Anote o IP do WebSocket exibido

### 5. Configurar Sistema de Detecção (2 min)

Edite `detection/modules/config.py`:

```python
# Câmera
CAMERA_ID = 0              # ID da sua câmera
CAMERA_WIDTH = 640
CAMERA_HEIGHT = 640
CAMERA_FPS = 60

# Modelo customizado
MODEL_PATH = "detection/models/below-trash-v2.pt"
CONFIDENCE_THRESHOLD = 0.15
TARGET_CLASSES = ['can', 'paper']  # Modelo customizado

# WebSocket do ESP32
API_URL = "ws://192.168.1.100:8000/ws/controller"  # IP do servidor
```

### 6. Executar Sistema (3 min)

**Terminal 1 - API Server:**
```bash
cd api
python api_server.py
# Deve mostrar: Server running on http://0.0.0.0:8000
```

**Terminal 2 - Detection:**
```bash
cd detection
python main.py
# Deve abrir janela da câmera
```

Pronto! 🎉 O sistema está funcionando!

## 🎮 Controles

| Tecla | Função |
|-------|--------|
| `ESC` | Sair do programa |
| `SPACE` | Pausar/Retomar detecção |
| `D` | Ativar/Desativar visualização 3D |

## 🧪 Testar Componentes

### Testar Câmera
```bash
python tests/test_camera.py
```

### Testar WebSocket
```bash
# Servidor
cd api
python api_server.py

# Cliente (outro terminal)
python -c "import websocket; ws = websocket.create_connection('ws://localhost:8000/ws/controller'); ws.send('V:0.5,0.3'); print('Enviado!'); ws.close()"
```

### Testar ESP32
```bash
# No Serial Monitor do ESP32, você deve ver mensagens quando enviar comandos
```

## ⚙️ Configuração Recomendada

Para melhor performance no PC:

```python
# detection/modules/config.py

# Câmera (640x640 recomendado para YOLO)
CAMERA_WIDTH = 640
CAMERA_HEIGHT = 640
CAMERA_FPS = 60

# Modelo (v2 é mais preciso)
MODEL_PATH = "detection/models/below-trash-v2.pt"
CONFIDENCE_THRESHOLD = 0.15

# Performance
MIN_TRACKING_FRAMES = 5  # Mínimo de frames para calcular velocidade
TRAJECTORY_POINTS = 20   # Pontos na visualização 3D

# Física
ROBOT_HEIGHT = 0.5  # 50cm de altura da "boca" do robô
GRAVITY = 9.81      # Gravidade padrão Terra
```

## 🐛 Problemas Comuns

### Câmera não funciona (Windows)
```powershell
# Verificar dispositivos disponíveis
python detection/tools/camera_selector.py

# Testar diferentes IDs
# Edite config.py: CAMERA_ID = 1 (ou 2, 3...)
```

### WebSocket não conecta
```bash
# 1. Verifique se servidor está rodando
# Terminal deve mostrar: Server running on...

# 2. Verifique firewall do Windows
# Permita Python e api_server.py

# 3. Verifique IP correto
ipconfig  # Windows
ifconfig  # Linux/Mac
```

### ESP32 não conecta no WiFi
```cpp
# Verifique Serial Monitor (115200 baud)
# Deve mostrar: WiFi connected! IP: ...

# Se não conectar:
// 1. Verifique SSID e senha
// 2. Verifique se WiFi é 2.4GHz (ESP32 não suporta 5GHz)
// 3. Aproxime ESP32 do roteador
```

### Modelo não detecta objetos
```python
# 1. Teste com imagens estáticas
python tests/test_yolo_classes.py

# 2. Diminua confiança (pode aumentar falsos positivos)
CONFIDENCE_THRESHOLD = 0.10

# 3. Verifique iluminação (ambiente bem iluminado)

# 4. Use modelo v1 se v2 não funcionar
MODEL_PATH = "detection/models/below-trash-v1.pt"
```

## 📚 Documentação Completa

- [README.md](../README.md) - Documentação completa do projeto
- [CLASSES.md](CLASSES.md) - Classes detectadas (can, paper)
- [PHYSICS.md](PHYSICS.md) - Física de trajetória
- [OPTIMIZATION.md](OPTIMIZATION.md) - Otimizações de performance
- [TROUBLESHOOTING.md](TROUBLESHOOTING.md) - Resolução detalhada de problemas
- [CarrinhoMovimentacao.md](CarrinhoMovimentacao.md) - Controle Mecanum

## 🎓 Próximos Passos

1. ✅ Sistema funcionando básico
2. 🎯 Teste com objetos reais (papeis, latinhas)
3. 📐 Calibre altura do robô em `config.py`
4. 🎨 Experimente modo desenvolvedor (tecla D)
5. ⚡ Otimize thresholds e parâmetros
6. 🤖 Ajuste controle do robô no ESP32

## 💡 Dicas Importantes

- **GPU é recomendada** - NVIDIA com CUDA acelera muito (mas CPU funciona)
- **Iluminação** - Ambiente bem iluminado = melhor detecção
- **Distância** - Calibre conforme distância real da câmera ao chão
- **Objetos reais** - Modelo foi treinado com papeis/latinhas reais
- **Modo DEV** - Use tecla D para ver trajetórias 3D

## 🆘 Precisa de Ajuda?

1. Veja [TROUBLESHOOTING.md](TROUBLESHOOTING.md)
2. Execute testes: `python tests/test_camera.py`
3. Verifique logs no terminal
4. Abra issue no GitHub com:
   - Logs completos
   - Sistema operacional
   - Versão Python
   - Hardware usado

---

**Tempo total**: ~20 minutos (excluindo download de dependências)

**FPS esperado**: 
- PC com GPU: 60+ FPS
- PC sem GPU: 20-30 FPS
- Laptop: 15-25 FPS

Boa sorte! 🚀
