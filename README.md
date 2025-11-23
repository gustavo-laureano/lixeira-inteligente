# 🗑️ Lixeira Inteligente - Sistema de Detecção Customizado

Este projeto consiste no desenvolvimento de um sistema robótico autônomo para interceptação de objetos em pleno voo. O núcleo do sistema utiliza visão computacional com um **modelo YOLO customizado** treinado especificamente para detectar **papeis amassados** e **latinhas**, otimizado para o cenário real de uso.

## 📋 Índice

- [Características](#características)
- [Modelo Customizado](#modelo-customizado)
- [Classes Detectadas](#classes-detectadas)
- [Requisitos](#requisitos)
- [Instalação](#instalação)
- [Configuração](#configuração)
- [Uso](#uso)
- [Comunicação com Arduino](#comunicação-com-arduino)
- [Otimizações](#otimizações)
- [Troubleshooting](#troubleshooting)

## ✨ Características

- ⚡ **Modelo customizado** treinado com dataset próprio
- 🎯 **Alta precisão** para papeis e latinhas em movimento
- 📹 **Câmera 640x640** otimizada para detecção em tempo real
- 🔌 **Comunicação WebSocket** com sistema de controle
- 🎨 **Visualização 3D** de trajetórias (modo desenvolvedor)
- ⚙️ **Configuração centralizada** - fácil customização
- 📊 **Predição física** de trajetória e ponto de impacto
- 🤖 **Modelo especializado** - 2 classes treinadas com imagens reais

## 🎯 Modelo Customizado

O sistema utiliza o modelo **below-trash-v2.pt**, treinado especificamente para este projeto com centenas de imagens de papeis amassados e latinhas em diferentes condições de iluminação, ângulos e velocidades.

### 📦 Dataset Próprio

- **Papeis amassados**: Diversos tamanhos, cores e níveis de amassamento
- **Latinhas**: Alumínio, diferentes marcas e condições
- **Cenários reais**: Movimento, blur, oclusões parciais
- **Augmentação**: Rotação, escala, iluminação, ruído

## 🎯 Classes Detectadas

O modelo customizado detecta **2 classes** específicas para o projeto:

| ID | Classe | Descrição | Tamanho Real |
|----|--------|-----------|--------------|
| 0 | `can` | Latinhas de alumínio | ~17cm altura |
| 1 | `paper` | Papeis amassados | ~10cm diâmetro |

### ✅ Vantagens do Modelo Customizado

- ✅ **Alta precisão** para os objetos específicos do projeto
- ✅ **Latinhas detectadas corretamente** (não confunde com garrafas)
- ✅ **Papeis amassados** detectados mesmo com deformações
- ✅ **Otimizado para movimento** - treinado com blur e motion
- ✅ **Leve e rápido** - ideal para dispositivos embarcados

## 🔧 Requisitos

### Hardware
- **PC ou Raspberry Pi** (recomendado PC com GPU para melhor performance)
- **Câmera USB** compatível (testado com webcams comuns)
- **ESP32 ou Arduino** (controle via WebSocket)
- **Rodas Mecanum** (4 rodas omnidirecionais)
- **2x TB6612FNG** (controladores de motor)

### Software
- **Python 3.11+** (versão utilizada no desenvolvimento)
- **PyTorch** com suporte CUDA (opcional, para GPU)
- **OpenCV** (cv2)
- **Ultralytics** (YOLOv8/v11)
- **NumPy, Matplotlib** (visualização 3D)
- **WebSocket** (comunicação com robô)

## 📥 Instalação

### 1. Clonar o Repositório

```bash
git clone https://github.com/gustavo-laureano/lixeira-inteligente.git
cd lixeira-inteligente
```

### 2. Instalar Dependências Python
_Recomendo utilizar a versão 3.11 do Python  devido a riscos de incompatibilidade._

```bash
# Criar ambiente virtual (recomendado)
python -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate  # Windows

# Instalar dependências
pip install -r requirements.txt
```

### 3. Verificar Câmera

```bash
# Listar câmeras disponíveis
python detection/tools/camera_selector.py

# Testar câmera
python tests/test_camera.py #altere 'device=0' para o id da camera em uso
```

### 4. Configurar ESP32/Arduino

1. Abra o projeto no PlatformIO
2. Configure os pinos em `include/Config.h`
3. Configure o IP do servidor no `APIreceiver.h` 
```
// Ajuste estes valores conforme seu ambiente
const char* SERVER_HOST = "10.212.20.30";  // IP do PC/Servidor com a API
const int   SERVER_PORT = 8000;
const char* SERVER_PATH = "/ws/robot";
#define WIFI_PASSWORD       "wifitop12347"
```
Configure a rede no `Config.h` 
```
// Configurações WiFi para APIreceiver
#define WIFI_SSID           "POCO M3 Pro 5G"
#define WIFI_PASSWORD       "wifitop12347"
```

4. Compile e faça upload para o ESP32
5. Anote o IP do WebSocket (será exibido no Serial)

## ⚙️ Configuração

### 1. Editar detection/modules/config.py

Ajuste as configurações conforme seu setup:

```python
# Câmera
CAMERA_ID = 0              # ID da câmera
CAMERA_WIDTH = 640         # Resolução
CAMERA_HEIGHT = 640
CAMERA_FPS = 60

# Modelo YOLO customizado
MODEL_PATH = "detection/models/below-trash-v1.pt"
CONFIDENCE_THRESHOLD = 0.15
TARGET_CLASSES = ['can', 'paper']  # Classes do modelo customizado

# Dimensões reais dos objetos (em metros)
OBJECT_DIMENSIONS = {
    0: 0.17,  # can - 17cm
    1: 0.10   # paper - 10cm
}

# WebSocket do robô
API_URL = "ws://192.168.x.x:8000/ws/controller"  # IP do ESP32

# Modo desenvolvedor (visualização 3D)
DEFAULT_DEV_MODE = True
```

## 🚀 Uso

### Executar Sistema Principal

```bash
# Ativar ambiente virtual
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows

# Executar detecção
python detection/main.py
```

### Controles do Teclado

| Tecla | Função |
|-------|--------|
| `ESC` | Sair do programa |
| `SPACE` | Pausar/Retomar detecção |
| `D` | Ativar/Desativar modo desenvolvedor (visualização 3D) |

### Modo Desenvolvedor

Ao pressionar `D`, uma janela 3D é aberta mostrando:
- 🔵 **Posição atual** do objeto detectado
- 🟢 **Ponto de impacto** previsto no chão
- 📈 **Trajetória completa** com física aplicada
- 📏 **Eixos 3D** com escala em metros

## 📊 Sistema de Predição

O sistema calcula:

1. **Posição 3D** do objeto usando geometria da câmera
2. **Velocidade** através de histórico de posições (regressão linear)
3. **Trajetória** aplicando física (gravidade 9.81 m/s²)
4. **Ponto de aterrissagem** resolvendo equação do movimento

### Fórmulas Utilizadas

- **Distância**: $Z = \frac{f \times W_{real}}{W_{pixel}}$
- **Trajetória**: $y(t) = y_0 + v_y \times t - \frac{1}{2} \times g \times t^2$
- **Impacto**: $t_{land} = \frac{v_y + \sqrt{v_y^2 + 2 \times g \times y_0}}{g}$
# Carrinho Movimentacao — Módulo de Movimentação (Mecanum)

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

