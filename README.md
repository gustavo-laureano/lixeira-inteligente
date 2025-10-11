# 🗑️ Lixeira Inteligente - Sistema YOLO para Raspberry Pi

Sistema de detecção de objetos em tempo real usando YOLOv8, otimizado para Raspberry Pi com câmera 480p e comunicação com Arduino.

## 📋 Índice

- [Características](#características)
- [Classes Detectadas](#classes-detectadas)
- [Requisitos](#requisitos)
- [Instalação](#instalação)
- [Configuração](#configuração)
- [Uso](#uso)
- [Comunicação com Arduino](#comunicação-com-arduino)
- [Otimizações](#otimizações)
- [Troubleshooting](#troubleshooting)

## ✨ Características

- ⚡ **Detecção rápida** com YOLOv8-nano (otimizado para ARM)
- 📹 **Câmera 480p** (640x480) para melhor performance
- 🔌 **Comunicação serial** com Arduino para controle de movimento
- 🐳 **Docker containerizado** para fácil deploy
- ⚙️ **Configuração via YAML** - fácil customização
- 📊 **Logging detalhado** para debug e monitoramento
- 🎯 **Detecção de múltiplas classes** (garrafas, copos, tigelas)
- 🤖 **Modelo pré-treinado** - detecta 80 objetos do COCO dataset automaticamente

## 🎯 Classes Detectadas

O YOLOv8 vem **pré-treinado** com o dataset COCO e já detecta **80 classes** automaticamente, sem necessidade de treinar nada!

### ✅ Classes Úteis para Lixeira:

| Classe | Descrição | Status |
|--------|-----------|--------|
| `bottle` | Garrafas PET, vidro | ✅ Recomendado |
| `cup` | Copos, xícaras | ✅ Recomendado |
| `bowl` | Tigelas, bowls | ✅ Recomendado |
| `wine glass` | Taças, cálices | ⚪ Opcional |
| `fork`, `knife`, `spoon` | Talheres | ⚪ Opcional |
| `banana`, `apple`, `orange` | Frutas | ⚪ Opcional |
| `can` | Latas | ❌ **NÃO disponível** |

> **⚠️ IMPORTANTE**: O dataset COCO **NÃO tem a classe "can" (lata)**. Latas cilíndricas são geralmente detectadas como `bottle`. Se precisar distinguir latas de garrafas, considere adicionar um sensor de metal ou treinar um modelo customizado.

### 📝 Testar Classes Disponíveis

Execute este comando para ver todas as 80 classes que o modelo detecta:

```bash
python3 test_yolo_classes.py
```

### 🔍 Classes COCO Completas (80 objetos):

```
person, bicycle, car, motorcycle, airplane, bus, train, truck, boat,
traffic light, fire hydrant, stop sign, parking meter, bench, bird,
cat, dog, horse, sheep, cow, elephant, bear, zebra, giraffe, backpack,
umbrella, handbag, tie, suitcase, frisbee, skis, snowboard, sports ball,
kite, baseball bat, baseball glove, skateboard, surfboard, tennis racket,
bottle, wine glass, cup, fork, knife, spoon, bowl, banana, apple,
sandwich, orange, broccoli, carrot, hot dog, pizza, donut, cake, chair,
couch, potted plant, bed, dining table, toilet, tv, laptop, mouse,
remote, keyboard, cell phone, microwave, oven, toaster, sink,
refrigerator, book, clock, vase, scissors, teddy bear, hair drier,
toothbrush
```

## 🔧 Requisitos

### Hardware
- **Raspberry Pi 3/4/5** (recomendado Pi 4 com 4GB RAM ou superior)
- **Câmera USB ou CSI** compatível com V4L2
- **Arduino** (qualquer modelo com comunicação serial)
- **Cabo USB** para conexão Arduino-Raspberry
- **Cartão SD** de pelo menos 16GB (recomendado 32GB)

### Software
- **Raspberry Pi OS** (64-bit recomendado)
- **Docker** e **Docker Compose**
- **Git**

## 📥 Instalação

### 1. Preparar o Raspberry Pi

```bash
# Atualizar sistema
sudo apt update && sudo apt upgrade -y

# Instalar Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Adicionar usuário ao grupo docker
sudo usermod -aG docker $USER

# Instalar Docker Compose
sudo apt install docker-compose -y

# Reiniciar para aplicar mudanças de grupo
sudo reboot
```

### 2. Clonar o Repositório

```bash
cd ~
git clone https://github.com/gustavo-laureano/lixeira-inteligente.git
cd lixeira-inteligente
```

### 3. Criar Diretórios Necessários

```bash
mkdir -p logs models data
```

### 4. Verificar Dispositivos

```bash
# Verificar câmera
ls -l /dev/video*

# Verificar porta serial do Arduino
ls -l /dev/ttyUSB* /dev/ttyACM*

# Testar câmera (instale v4l-utils se necessário)
sudo apt install v4l-utils
v4l2-ctl --list-devices
```

## ⚙️ Configuração

### 1. Editar config.yaml

Abra o arquivo `config.yaml` e ajuste conforme seu setup:

```yaml
camera:
  resolution: [640, 480]  # Resolução 480p
  fps: 30                  # FPS desejado
  device: 0                # Device da câmera

serial:
  port: "/dev/ttyUSB0"    # Porta do Arduino
  baudrate: 9600           # Baudrate (igual ao Arduino)

detection:
  classes:                 # Classes a detectar
    - "bottle"
    - "cup"
    - "can"
  min_area: 1000          # Área mínima em pixels
```

### 2. Ajustar docker-compose.yml

Verifique os dispositivos no `docker-compose.yml`:

```yaml
devices:
  - /dev/video0:/dev/video0      # Ajuste se necessário
  - /dev/ttyUSB0:/dev/ttyUSB0    # Ajuste conforme sua porta
```

## 🚀 Uso

### Build da Imagem

```bash
docker-compose build
```

**Nota:** O primeiro build pode demorar 30-60 minutos no Raspberry Pi.

### Executar o Sistema

```bash
# Iniciar em background
docker-compose up -d

# Ver logs em tempo real
docker-compose logs -f

# Parar o sistema
docker-compose down
```

### Executar Sem Docker (Desenvolvimento)

```bash
# Instalar dependências
pip3 install -r requirements.txt

# Executar
python3 detect.py
```

## 🔌 Comunicação com Arduino

### Formato dos Comandos

O sistema envia comandos no formato:

```
CLASSE:POSIÇÃO:DISTÂNCIA
```

**Posições:**
- `LEFT` - Objeto à esquerda
- `CENTER` - Objeto no centro
- `RIGHT` - Objeto à direita

**Distâncias (baseadas na área do objeto em pixels):**
- `VERY_CLOSE` - Muito perto (área > 50.000 pixels²) → **Arduino RECUA**
- `CLOSE` - Perto (área > 20.000 pixels²) → Arduino para (objeto alcançado)
- `MEDIUM` - Distância média (área > 10.000 pixels²) → Arduino avança devagar
- `FAR` - Longe (área < 10.000 pixels²) → Arduino avança rápido

Exemplos:
- `BOTTLE:LEFT:FAR` - Garrafa longe à esquerda (vira esquerda + avança rápido)
- `CAN:CENTER:MEDIUM` - Lata média distância no centro (avança devagar)
- `CUP:RIGHT:CLOSE` - Copo perto à direita (para/ajusta)
- `BOWL:CENTER:VERY_CLOSE` - Tigela muito perto no centro (**RECUA**)

### Código Arduino Exemplo

```cpp
void setup() {
  Serial.begin(9600);
  // Configurar seus motores aqui
}

void loop() {
  if (Serial.available() > 0) {
    String command = Serial.readStringUntil('\n');
    processCommand(command);
  }
}

void processCommand(String cmd) {
  // Parse: OBJETO:POSICAO:DISTANCIA
  int firstColon = cmd.indexOf(':');
  int secondColon = cmd.indexOf(':', firstColon + 1);
  
  String object = cmd.substring(0, firstColon);
  String position = cmd.substring(firstColon + 1, secondColon);
  String distance = cmd.substring(secondColon + 1);
  
  // Lógica baseada na DISTÂNCIA
  if (distance == "VERY_CLOSE") {
    // ⬅️ RECUAR - Objeto muito perto!
    moveBackward();
    
  } else if (distance == "CLOSE") {
    // ⏸️ PARAR - Objeto alcançado!
    stopMotors();
    
  } else if (distance == "MEDIUM") {
    // 🐢 APROXIMAR DEVAGAR
    if (position == "LEFT") {
      turnLeft();
      moveForwardSlow();
    } else if (position == "RIGHT") {
      turnRight();
      moveForwardSlow();
    } else {
      moveForwardSlow();
    }
    
  } else if (distance == "FAR") {
    // 🚀 AVANÇAR RÁPIDO
    if (position == "LEFT") {
      turnLeft();
      moveForwardFast();
    } else if (position == "RIGHT") {
      turnRight();
      moveForwardFast();
    } else {
      moveForwardFast();
    }
  }
  
  Serial.println("OK"); // Resposta
}
```

Veja o código completo em [arduino_example.ino](arduino_example.ino).

## ⚡ Otimizações para Performance

### 1. Usar Modelo Nano

O YOLOv8n (nano) é o mais rápido. Modelos maiores são muito lentos no Raspberry Pi:
- ✅ `yolov8n.pt` - **Recomendado** (~10-15 FPS no Pi 4)
- ⚠️ `yolov8s.pt` - Mais lento (~3-5 FPS)
- ❌ `yolov8m.pt`, `yolov8l.pt` - Muito lentos

### 2. Reduzir Resolução

Se precisar de mais FPS, reduza a resolução:

```yaml
camera:
  resolution: [320, 240]  # QVGA - mais rápido
```

### 3. Skip Frames

Processe apenas alguns frames:

```yaml
performance:
  frame_skip: 2  # Processa 1 a cada 2 frames
```

### 4. Aumentar Confidence Threshold

Reduza falsos positivos aumentando a confiança mínima:

```yaml
yolo:
  confidence: 0.6  # Maior = menos detecções mas mais precisas
```

### 5. Overclock do Raspberry Pi (Opcional)

**ATENÇÃO:** Faça apenas se tiver boa ventilação!

Edite `/boot/config.txt`:

```bash
# Para Raspberry Pi 4
over_voltage=6
arm_freq=2000
gpu_freq=750
```

## 🐛 Troubleshooting

### Câmera não detectada

```bash
# Verificar se câmera está conectada
vcgencmd get_camera

# Testar câmera
raspistill -o test.jpg  # Para câmera CSI
fswebcam test.jpg       # Para câmera USB

# Verificar permissões
sudo chmod 666 /dev/video0
```

### Arduino não comunica

```bash
# Verificar porta
ls -l /dev/ttyUSB* /dev/ttyACM*

# Adicionar permissões
sudo usermod -aG dialout $USER

# Testar comunicação
sudo apt install screen
screen /dev/ttyUSB0 9600
```

### Performance muito baixa

1. **Reduzir resolução** para 320x240
2. **Usar frame_skip** = 2 ou 3
3. **Aumentar min_area** para ignorar objetos pequenos
4. **Verificar temperatura**: `vcgencmd measure_temp`
5. **Adicionar dissipador de calor** e ventilador

### Docker build falha

```bash
# Limpar cache
docker system prune -a

# Build sem cache
docker-compose build --no-cache

# Verificar espaço em disco
df -h
```

### Modelo YOLO não baixa

```bash
# Baixar manualmente
cd models
wget https://github.com/ultralytics/assets/releases/download/v0.0.0/yolov8n.pt
```

## 📊 Monitoramento

### Ver logs

```bash
# Logs em tempo real
docker-compose logs -f

# Últimas 100 linhas
docker-compose logs --tail=100

# Arquivo de log
tail -f logs/detection.log
```

### Estatísticas do Container

```bash
# Uso de recursos
docker stats lixeira-inteligente

# Informações do container
docker inspect lixeira-inteligente
```

## 🔄 Atualização

```bash
# Parar sistema
docker-compose down

# Atualizar código
git pull

# Rebuild e reiniciar
docker-compose up -d --build
```

## 📝 Estrutura do Projeto

```
lixeira-inteligente/
├── Dockerfile              # Imagem Docker
├── docker-compose.yml      # Orquestração
├── detect.py              # Script principal
├── config.yaml            # Configurações
├── requirements.txt       # Dependências Python
├── README.md             # Este arquivo
├── logs/                 # Logs do sistema
├── models/               # Modelos YOLO
└── data/                 # Dados e capturas
```

## 🤝 Contribuindo

Contribuições são bem-vindas! Por favor:

1. Fork o projeto
2. Crie uma branch para sua feature
3. Commit suas mudanças
4. Push para a branch
5. Abra um Pull Request

## 📄 Licença

Este projeto está sob a licença MIT. Veja o arquivo LICENSE para detalhes.

## 👨‍💻 Autor

**Gustavo Laureano**

- GitHub: [@gustavo-laureano](https://github.com/gustavo-laureano)

## 🙏 Agradecimentos

- [Ultralytics](https://github.com/ultralytics/ultralytics) pelo YOLOv8
- Comunidade Raspberry Pi
- Comunidade Arduino

---

**Dica:** Para melhor performance, use Raspberry Pi 4 com 4GB+ RAM e um bom sistema de refrigeração! 🌡️
