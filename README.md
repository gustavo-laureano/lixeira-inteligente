# 🗑️ Lixeira Inteligente - Sistema YOLO para Raspberry Pi

Este projeto consiste no desenvolvimento de um sistema robótico autônomo para interceptação de objetos em pleno voo. O núcleo do sistema utiliza visão computacional, implementando o modelo YOLO (You Only Look Once) para detecção e rastreamento de alta velocidade.

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
# CarrinhoMovimentacao — Módulo de Movimentação (Mecanum)

Sistema de controle (módulo) para movimentação de um carrinho com 4 rodas mecanum. Este repositório contém a parte responsável pelo controle de movimento (motores e entrada de comandos).

## 📋 Características

- **4 Rodas Mecanum**: Movimento omnidirecional completo
- **Arquitetura Modular**: Fácil expansão para novos controles
- **Controle via Dabble**: Interface mobile intuitiva
- **Movimentos Suportados**: 
  - Frente/Trás/Esquerda/Direita
  - Movimentos diagonais
  - Rotação no próprio eixo
  - Controle de velocidade

## 🏗️ Arquitetura

```
📁 include/
├── Config.h                 # Configurações centralizadas
├── InputController.h        # Interface base para controles
├── DabbleInputController.h  # Implementação Dabble
├── MecanumDrive.h          # Controle das rodas
└── SerialInputController.h  # Exemplo de expansão

📁 src/
└── main.cpp                # Código principal
```

## 🔧 Configuração do Hardware

### Hardware Utilizado:
- **2x TB6612FNG** (cada controlador gerencia 2 motores)
- **ESP32** para controle
- **4 Motores DC** com rodas mecanum

### ⚡ Alimentação:
- **VM (TB6612FNG):** 7.7V (alimentação dos motores)
- **VCC (TB6612FNG):** 5V (lógica do controlador) 
- **ESP32:** 3.3V ou via USB

⚠️ **IMPORTANTE:** Não alimente o ESP32 com 3.8V! Use 3.3V ou USB (5V)

### Motores (2x TB6612FNG):

**TB6612FNG #1 (Motores A e C):**
```cpp
// Motor A (Frontal Esquerdo) - Canal A do TB6612FNG #1
#define MOTOR_A_PWM_PIN    14  // PWMA - Marrom
#define MOTOR_A_DIR1_PIN   26  // AIN1 - Verde  
#define MOTOR_A_DIR2_PIN   27  // AIN2 - Amarelo

// Motor C (Frontal Direito) - Canal B do TB6612FNG #1
#define MOTOR_C_PWM_PIN    17  // PWMB - Amarelo
#define MOTOR_C_DIR1_PIN   18  // BIN1 - Branco
#define MOTOR_C_DIR2_PIN   19  // BIN2 - Marrom
```

**TB6612FNG #2 (Motores B e D):**
```cpp
// Motor B (Traseiro Esquerdo) - Canal A do TB6612FNG #2
#define MOTOR_B_PWM_PIN    32  // PWMA - Cinza
#define MOTOR_B_DIR1_PIN   25  // AIN1 - Roxo
#define MOTOR_B_DIR2_PIN   33  // AIN2 - Azul

// Motor D (Traseiro Direito) - Canal B do TB6612FNG #2
#define MOTOR_D_PWM_PIN    21  // PWMB - Roxo
#define MOTOR_D_DIR1_PIN   22  // BIN1 - Azul
#define MOTOR_D_DIR2_PIN   23  // BIN2 - Verde
```

### 🔌 Conexões TB6612FNG:
- **STBY:** Conecte ao VCC (sempre ativo) ou a um pino digital para controle
- **VM:** 7.7V (alimentação dos motores)
- **VCC:** 5V (lógica do controlador)
- **GND:** Terra comum

### Disposição das Rodas:
```
A ---- C
|  \  /  |
|   \/   |  
|   /\   |
|  /  \  |
B ---- D
```

## 🎮 Controles Disponíveis

### Dabble App (Bluetooth)

- **⬆️⬇️⬅️➡️**: Movimento direcional
- **⬆️+⬅️/➡️**: Movimentos diagonais
- **⬇️+⬅️/➡️**: Movimentos diagonais traseiros
- **⬜ (Square)**: Rotação esquerda
- **⭕ (Circle)**: Rotação direita  
- **🔺 (Triangle)**: Aumentar velocidade
- **❌ (Cross)**: Diminuir velocidade
- **SELECT**: Alternar GamePad ↔ Joystick

### 📟 Controle Serial (Monitor Serial)

Para usar controle serial, substitua `DabbleInputController` por `SerialInputController` no main.cpp.

#### Comandos de Movimento:
| Tecla | Ação | Emoji |
|-------|------|-------|
| `w` | Frente | ⬆️ |
| `s` | Trás | ⬇️ |
| `a` | Esquerda | ⬅️ |
| `d` | Direita | ➡️ |
| `q` | Girar Esquerda | 🔄 |
| `e` | Girar Direita | 🔃 |
| `x` | Parar | ⏹️ |

#### Comandos Diagonais:
| Tecla | Ação | Emoji |
|-------|------|-------|
| `r` | Frente-Direita | ↗️ |
| `t` | Frente-Esquerda | ↖️ |
| `f` | Trás-Direita | ↘️ |
| `g` | Trás-Esquerda | ↙️ |

#### Velocidades Predefinidas:
| Tecla | Velocidade | Valor | Emoji |
|-------|------------|-------|-------|
| `1` | Devagar | 80 | 🐢 |
| `2` | Normal | 140 | 🚶 |
| `3` | Rápido | 180 | 🏃 |
| `4` | Muito Rápido | 200 | 🚀 |

#### Ajuste Manual:
| Tecla | Ação | Emoji |
|-------|------|-------|
| `+` | Aumentar velocidade (+20) | ⬆️ |
| `-` | Diminuir velocidade (-20) | ⬇️ |

**Exemplo de uso:**
```
1     # Define velocidade devagar
w     # Move para frente devagar
3     # Muda para rápido  
r     # Move diagonal frente-direita rápido
x     # Para
```

## 🚀 Como Expandir

### Adicionando um Novo Controlador

1. **Crie uma nova classe** herdando de `BaseInputController`:

```cpp
class MeuNovoController : public BaseInputController {
public:
  MeuNovoController() : BaseInputController("Meu Controle") {}
  
  virtual bool begin() override {
    // Sua inicialização aqui
    return true;
  }
  
  virtual void update() override {
    // Lógica de atualização aqui
    // Use setMovementData() para enviar comandos
  }
};
```

2. **No main.cpp**, substitua a instanciação:

```cpp
// Era:
inputController = new DabbleInputController();

// Fica:
inputController = new MeuNovoController();
```

### Exemplos de Expansão

- **Serial**: Comandos via monitor serial
- **WiFi**: Interface web para controle
- **Joystick**: Controle analógico
- **IMU**: Controle por inclinação
- **Voz**: Comandos de voz
- **Câmera**: Seguir objetos/cores

## 🔧 Compilação

1. Abra o projeto no PlatformIO
2. Configure os pinos em `Config.h`
3. Compile e upload para o ESP32
4. Conecte via Dabble App

## 📊 Debug

O sistema fornece informações detalhadas via Serial:
- Status de conexão
- Comandos recebidos
- Estado dos motores
- Informações de sistema

## ⚙️ Configurações Avançadas

Edite `Config.h` para ajustar:
- Pinos dos motores
- Velocidades padrão
- Timeouts
- Configurações PWM
- Nome do dispositivo Bluetooth

## 🛠️ Solução de Problemas

1. **Motores não respondem**: Verifique conexões e pinos
2. **Movimento incorreto**: Ajuste a orientação dos motores
3. **Bluetooth não conecta**: Verifique o nome do dispositivo
4. **Velocidade baixa**: Ajuste `DEFAULT_SPEED` em Config.h

## 📈 Roadmap

- [ ] Controle via WiFi
- [ ] Interface web
- [ ] Sensores de obstáculos
- [ ] Controle autônomo
- [ ] Telemetria avançada

---

**Desenvolvido em 2025** 🚀
>>>>>>> 7b14a6e (Prepare project for GitHub: add main, cleanup backups, .gitignore, CI workflow)
