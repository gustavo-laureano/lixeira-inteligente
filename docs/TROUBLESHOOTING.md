# 🔧 Guia de Troubleshooting

Soluções para problemas comuns ao executar o sistema de Lixeira Inteligente.

## 📹 Problemas com Câmera

### ❌ Câmera não detectada

**Sintomas:**
```
Erro: Não foi possível abrir a câmera
Could not open camera 0
```

**Soluções:**

**Windows:**
```powershell
# 1. Verificar dispositivos disponíveis
python detection/tools/camera_selector.py

# 2. Testar diferentes IDs
# Edite config.py: CAMERA_ID = 1  # ou 2, 3...

# 3. Verificar permissões
# Windows Settings -> Privacy -> Camera -> Allow apps

# 4. Desativar aplicativos que usam câmera
# Feche Teams, Zoom, Discord, etc.
```

**Linux:**
```bash
# Verificar dispositivos
ls -l /dev/video*
v4l2-ctl --list-devices

# Permissões
sudo usermod -aG video $USER
sudo chmod 666 /dev/video0

# Testar câmera
ffplay /dev/video0
```

**Mac:**
```bash
# Verificar permissões
# System Preferences -> Security & Privacy -> Camera

# Testar câmera
python -c "import cv2; cap = cv2.VideoCapture(0); print('OK' if cap.isOpened() else 'ERRO')"
```

### ❌ Imagem preta ou congelada

**Soluções:**

```python
# 1. Aumentar timeout em camera_manager.py
time.sleep(2)  # Aguarda câmera inicializar

# 2. Verificar iluminação (precisa de luz!)

# 3. Testar resolução diferente em config.py
CAMERA_WIDTH = 640
CAMERA_HEIGHT = 480  # Tente diferentes

# 4. Resetar câmera
# Desconecte e reconecte USB
```

### ❌ FPS muito baixo

Ver [OPTIMIZATION.md](OPTIMIZATION.md) para detalhes completos.

**Verificações rápidas:**

```python
# 1. Verificar se GPU está sendo usada
import torch
print(f"CUDA: {torch.cuda.is_available()}")

# 2. Reduzir resolução em config.py
CAMERA_WIDTH = 416
CAMERA_HEIGHT = 416

# 3. Desativar visualização 3D
# Pressione D durante execução
# Ou: DEFAULT_DEV_MODE = False

# 4. Fechar programas pesados (Chrome, Discord, etc)
```

## 🌐 Problemas com WebSocket

### ❌ Servidor não inicia

**Sintomas:**
```
Error: Address already in use
```

**Soluções:**

**Windows:**
```powershell
# 1. Verificar se porta 8000 está em uso
netstat -ano | findstr :8000

# 2. Matar processo
taskkill /PID <PID> /F

# 3. Usar porta diferente
# Edite api_server.py: port=8001
```

**Linux:**
```bash
# Verificar porta
sudo lsof -i :8000

# Matar processo
kill -9 <PID>
```

### ❌ Cliente não conecta no servidor

**Sintomas:**
```
Connection refused
WebSocket connection failed
```

**Soluções:**

```bash
# 1. Verificar se servidor está rodando
cd api
python api_server.py
# Deve mostrar: Server running on http://0.0.0.0:8000

# 2. Verificar firewall (Windows)
# Windows Defender Firewall -> Allow an app
# Adicione Python

# 3. Verificar IP correto
ipconfig  # Windows
ifconfig  # Linux/Mac

# 4. Testar conexão local primeiro
# config.py: API_URL = "ws://localhost:8000/ws/controller"

# 5. Verificar antivírus (pode bloquear WebSocket)
```

### ❌ ESP32 não recebe comandos

**Sintomas:**
- Detection envia comandos
- ESP32 não responde

**Soluções:**

```cpp
// 1. Verificar Serial Monitor ESP32 (115200 baud)
// Deve mostrar: WebSocket connected!

// 2. Verificar configuração em APIreceiver.h
const char* SERVER_HOST = "192.168.1.100";  // IP DO SEU PC
const int SERVER_PORT = 8000;
const char* SERVER_PATH = "/ws/robot";

// 3. Testar conectividade
// No Serial Monitor ESP32: deve mostrar mensagens quando conecta

// 4. Verificar se está na mesma rede WiFi
```

## 🤖 Problemas com ESP32

### ❌ ESP32 não conecta no WiFi

**Sintomas:**
```
WiFi connection failed
Connecting to WiFi...
```

**Soluções:**

```cpp
// 1. Verificar SSID e senha em Config.h
#define WIFI_SSID "SUA_REDE"
#define WIFI_PASSWORD "SUA_SENHA"

// 2. Verificar se WiFi é 2.4GHz
// ESP32 NÃO suporta 5GHz!

// 3. Aproximar ESP32 do roteador

// 4. Adicionar delay em main.cpp
WiFi.begin(WIFI_SSID, WIFI_PASSWORD);
delay(5000);  // Aguarda 5 segundos

// 5. Resetar ESP32
// Botão RESET ou desconectar/reconectar USB
```

### ❌ Upload ESP32 falha

**Sintomas:**
```
Failed to connect to ESP32
Timed out waiting for packet header
```

**Soluções:**

```bash
# 1. Segurar botão BOOT durante upload
# Segurar BOOT, clicar Upload, soltar quando começar

# 2. Verificar porta COM correta
# PlatformIO: Ajuste em platformio.ini
upload_port = COM3  # Windows
upload_port = /dev/ttyUSB0  # Linux

# 3. Instalar drivers CH340/CP2102
# Windows: Baixe drivers USB-Serial

# 4. Verificar cabo USB
# Use cabo com DADOS (não só alimentação)

# 5. Reduzir upload_speed
upload_speed = 115200  # Ao invés de 921600
```

### ❌ ESP32 reinicia constantemente

**Sintomas:**
```
Brownout detector was triggered
Guru Meditation Error
```

**Soluções:**

```cpp
// 1. Alimentação insuficiente
// Use fonte 5V 2A+ (não USB do PC)

// 2. Adicionar capacitor 100µF entre VIN e GND

// 3. Verificar consumo dos motores
// Motores devem ter alimentação separada (7.7V)

// 4. Desabilitar brownout detector (último recurso)
// platformio.ini:
board_build.f_flash = 40000000L
board_build.flash_mode = dio
```

## 🧠 Problemas com YOLO / Detecção

### ❌ Modelo não baixa

**Sintomas:**
```
Error downloading model
URLError: <urlopen error [Errno 11001] getaddrinfo failed>
```

**Soluções:**

```bash
# 1. Verificar conexão internet
ping google.com

# 2. Baixar modelo manualmente
cd detection/models
# Download: https://github.com/ultralytics/assets/releases

# 3. Usar modelo local (se já tiver)
# config.py:
MODEL_PATH = "detection/models/below-trash-v2.pt"
```

### ❌ Não detecta objetos

**Sintomas:**
- Câmera funciona
- Nenhuma detecção aparece

**Soluções:**

```python
# 1. Reduzir confidence threshold
CONFIDENCE_THRESHOLD = 0.05  # Muito baixo para debug

# 2. Verificar se objeto está nas classes
TARGET_CLASSES = ['can', 'paper']  # Modelo customizado

# 3. Melhorar iluminação
# Ambiente BEM iluminado é essencial

# 4. Verificar se modelo está carregado
# Terminal deve mostrar: Modelo carregado: below-trash-v2.pt

# 5. Testar com imagem estática
python -c "from ultralytics import YOLO; m = YOLO('detection/models/below-trash-v2.pt'); m('test.jpg').show()"

# 6. Usar modelo v1 se v2 falhar
MODEL_PATH = "detection/models/below-trash-v1.pt"
```

### ❌ Detecções ruins/inconsistentes

**Soluções:**

```python
# 1. Ajustar confidence
CONFIDENCE_THRESHOLD = 0.15  # Balanceado
CONFIDENCE_THRESHOLD = 0.10  # Mais sensível
CONFIDENCE_THRESHOLD = 0.25  # Mais conservador

# 2. Aumentar resolução
CAMERA_WIDTH = 640
CAMERA_HEIGHT = 640

# 3. Verificar iluminação
# - Evite contra-luz
# - Use luz uniforme
# - Não aponte para janelas

# 4. Calibrar dimensões dos objetos
OBJECT_DIMENSIONS = {
    0: 0.17,  # can - Medir objeto real!
    1: 0.10   # paper - Ajustar conforme seu papel
}
```

### ❌ Memória insuficiente

**Sintomas:**
```
RuntimeError: CUDA out of memory
MemoryError
```

**Soluções:**

```python
# 1. Reduzir resolução
CAMERA_WIDTH = 416
CAMERA_HEIGHT = 416

# 2. Usar CPU ao invés de GPU
# config.py ou main.py:
device = 'cpu'

# 3. Reduzir histórico de tracking
MAX_HISTORY = 10

# 4. Fechar programas
# Chrome, Discord, etc

# 5. Reiniciar Python
```

## 🎨 Problemas com Visualização 3D

### ❌ Janela 3D não abre

**Sintomas:**
- Pressiona D
- Nada acontece

**Soluções:**

```python
# 1. Verificar se matplotlib está instalado
pip install matplotlib

# 2. Verificar backend
import matplotlib
print(matplotlib.get_backend())
# Deve ser: TkAgg, Qt5Agg, ou WXAgg

# 3. Instalar backend (se necessário)
pip install PyQt5
# Ou
pip install tk

# 4. Testar matplotlib
python -c "import matplotlib.pyplot as plt; plt.plot([1,2]); plt.show()"
```

### ❌ Visualização 3D muito lenta

**Soluções:**

```python
# 1. Desativar por padrão
DEFAULT_DEV_MODE = False

# 2. Reduzir pontos da trajetória
TRAJECTORY_POINTS = 10  # Ao invés de 20

# 3. Aumentar intervalo de atualização
# Edite vision.py: blit=True para animação mais rápida

# 4. Usar janela menor
```

## 📊 Problemas de Performance

### ❌ Sistema lento/lag

**Diagnóstico:**

```python
# 1. Monitorar FPS
# Terminal mostra: [FPS: XX.X]

# 2. Verificar uso de GPU
# Windows: Task Manager -> Performance -> GPU
# Linux: nvidia-smi

# 3. Verificar uso de CPU
# Windows: Task Manager
# Linux: htop

# 4. Verificar temperatura
# GPU >85°C = throttling
```

**Soluções:** Ver [OPTIMIZATION.md](OPTIMIZATION.md)

### ❌ Alta latência de resposta

**Sintomas:**
- Detecção funciona
- Robô responde com delay

**Soluções:**

```python
# 1. Reduzir MIN_TRACKING_FRAMES
MIN_TRACKING_FRAMES = 3  # Mais rápido, menos preciso

# 2. Usar rede mais rápida (WiFi 5GHz ou Ethernet)

# 3. Otimizar código ESP32
// Evite delays desnecessários
// Use processamento não-bloqueante

# 4. Reduzir FPS da câmera se necessário
CAMERA_FPS = 30

# 5. Verificar latência de rede
ping 192.168.1.100  # IP do ESP32
```

## 💻 Problemas de Sistema

### ❌ Import errors (Python)

**Sintomas:**
```
ModuleNotFoundError: No module named 'ultralytics'
```

**Soluções:**

```bash
# 1. Ativar ambiente virtual
# Windows:
venv\Scripts\activate

# Linux/Mac:
source venv/bin/activate

# 2. Reinstalar dependências
pip install -r requirements.txt

# 3. Verificar versão Python
python --version
# Deve ser 3.8+, recomendado 3.11

# 4. Criar novo ambiente virtual
python -m venv venv_novo
venv_novo\Scripts\activate
pip install -r requirements.txt
```

### ❌ Python não encontrado (Windows)

**Soluções:**

```powershell
# 1. Adicionar Python ao PATH
# Windows: Configurações -> Sistema -> Variáveis de Ambiente

# 2. Reinstalar Python
# Download: https://www.python.org/downloads/
# ✅ Marcar "Add Python to PATH" durante instalação

# 3. Usar py ao invés de python
py -m pip install -r requirements.txt
py detection/main.py
```

### ❌ Permissões negadas (Linux)

```bash
# Câmera
sudo usermod -aG video $USER

# Serial
sudo usermod -aG dialout $USER

# Aplicar (precisa logout/login)
newgrp video
newgrp dialout
```

## 🔍 Debug Avançado

### Modo Verbose

```python
# config.py
import logging
logging.basicConfig(level=logging.DEBUG)
```

### Logs Detalhados

```bash
# Redirecionar para arquivo
python detection/main.py > log.txt 2>&1

# Ver logs em tempo real
tail -f log.txt  # Linux/Mac
Get-Content log.txt -Wait  # Windows PowerShell
```

### Testar Componentes Isoladamente

```bash
# Apenas câmera
python tests/test_camera.py

# Apenas modelo YOLO
python tests/test_yolo_classes.py

# Apenas WebSocket
cd api
python api_server.py
# Outro terminal:
python -c "import websocket; ws=websocket.create_connection('ws://localhost:8000/ws/controller'); ws.send('test'); ws.close()"
```

## 📞 Checklist de Verificação

Antes de pedir ajuda, verifique:

- [ ] Python 3.8+ instalado
- [ ] Ambiente virtual ativado
- [ ] Dependências instaladas (`pip install -r requirements.txt`)
- [ ] Câmera conectada e funcionando
- [ ] Modelo `below-trash-v2.pt` existe em `detection/models/`
- [ ] Config.py configurado (CAMERA_ID, API_URL)
- [ ] Firewall permite Python
- [ ] ESP32 conectado no WiFi (verificar Serial Monitor)
- [ ] API Server rodando (`python api/api_server.py`)
- [ ] Iluminação adequada no ambiente

## 🆘 Ainda com problemas?

### 1. Coletar informações

```bash
# Sistema
python --version
pip list

# GPU (se tiver)
python -c "import torch; print(f'CUDA: {torch.cuda.is_available()}')"

# Logs
python detection/main.py > debug.log 2>&1
```

### 2. Abrir Issue no GitHub

Inclua:
- Sistema operacional (Windows 10/11, Ubuntu 22.04, etc)
- Versão Python
- Hardware (CPU/GPU)
- Logs completos
- Passos para reproduzir
- Configurações usadas

### 3. Documentação

- [README.md](../README.md) - Documentação completa
- [QUICKSTART.md](QUICKSTART.md) - Guia rápido
- [OPTIMIZATION.md](OPTIMIZATION.md) - Otimizações
- [PHYSICS.md](PHYSICS.md) - Física do sistema

---

**Dica:** A maioria dos problemas é causada por:
1. 📹 **Câmera** não configurada/permissões (40%)
2. 🌐 **WebSocket** firewall/IP errado (30%)
3. 🐍 **Python** ambiente virtual não ativado (20%)
4. 💡 **Iluminação** ruim no ambiente (10%)

Sempre comece verificando estes 4 pontos! ✅
