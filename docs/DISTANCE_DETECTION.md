# 📏 Sistema de Detecção 3D e Predição de Trajetória

## 🎯 Visão Geral

Este sistema **não usa área de pixels** para estimar distância. Ao invés disso, utiliza **geometria de câmera** e **física** para calcular:

1. **Posição 3D** do objeto no espaço (x, y, z)
2. **Velocidade 3D** através de tracking temporal
3. **Trajetória futura** aplicando física (gravidade)
4. **Ponto de aterrissagem** onde o objeto vai cair

## 📐 Como Funciona

### 1. Câmera Pinhole Model

A câmera funciona como uma **câmera pinhole** (modelo de projeção perspectiva):

```
Objeto Real (3D)  →  Projeção na Imagem (2D)
      ↓
   Câmera
      ↓
   Cálculo reverso (2D → 3D)
```

### 2. Fórmula de Distância

$$Z = \frac{f \times W_{real}}{W_{pixel}}$$

**Onde:**
- **Z** = Distância do objeto à câmera (metros)
- **f** = Distância focal da câmera (pixels)
- **W_real** = Largura real do objeto (metros)
- **W_pixel** = Largura do objeto na imagem (pixels)

### 3. Conversão 2D → 3D

```python
# Dado um objeto detectado no frame:
x_pixel, y_pixel, width_pixel, height_pixel = bbox

# 1. Calcular distância (Z)
Z = (focal_length * real_width) / width_pixel

# 2. Calcular X (esquerda/direita)
X = (x_pixel - center_x) * Z / focal_length

# 3. Calcular Y (profundidade)
Y = Z  # Distância da câmera

# Resultado: Posição 3D = (X, Y, Z)
```

**Exemplo:**
```
Latinha detectada:
- Largura na imagem: 50 pixels
- Largura real: 0.06m (6cm)
- Focal length: 500 pixels

Z = (500 * 0.06) / 50 = 0.6 metros

A latinha está a 60cm da câmera!
```

## 📊 Sistema de Coordenadas

### Referencial

```
        Z (Altura)
        ↑
        |
        |
        o----→ X (Esquerda/Direita)
       /
      ↙
     Y (Profundidade/Distância)
```

**Convenção:**
- **X = 0**: Centro da câmera
- **X < 0**: Objeto à esquerda
- **X > 0**: Objeto à direita
- **Y**: Distância frontal da câmera
- **Z = 0**: Chão
- **Z > 0**: Altura acima do chão

### Exemplo Visual

```
Câmera no topo olhando para baixo:

         Y (distância)
         ↑
         |
    -X ← o → +X
         |
         ↓
```

Um objeto em `(0.2, 1.5, 1.0)` está:
- **20cm à direita** da câmera
- **1.5m de distância** (profundidade)
- **1m de altura** do chão

## 🎯 Cálculo de Velocidade

### Tracking Temporal

O sistema mantém **histórico de posições** para calcular velocidade:

```python
# Posições detectadas ao longo do tempo
t0 = 0.0s: posição = (0.0, 1.5, 2.0)
t1 = 0.1s: posição = (0.1, 1.6, 1.9)
t2 = 0.2s: posição = (0.2, 1.7, 1.7)
t3 = 0.3s: posição = (0.3, 1.8, 1.4)

# Velocidade = variação da posição / tempo
vx = (0.3 - 0.0) / 0.3 = 1.0 m/s (movendo para direita)
vy = (1.8 - 1.5) / 0.3 = 1.0 m/s (se afastando)
vz = (1.4 - 2.0) / 0.3 = -2.0 m/s (caindo)
```

### Regressão Linear

Para maior precisão, usa **regressão linear** nos últimos N frames:

```python
# Ajusta uma linha aos pontos históricos
slope_x, intercept_x = linear_regression(times, positions_x)
slope_y, intercept_y = linear_regression(times, positions_y)
slope_z, intercept_z = linear_regression(times, positions_z)

# Slopes são as velocidades
vx = slope_x  # m/s
vy = slope_y  # m/s
vz = slope_z  # m/s
```

**Vantagem:** Suaviza ruído de detecção!

## 🌍 Física da Trajetória

### Equações do Movimento

Uma vez conhecendo posição `(x, y, z)` e velocidade `(vx, vy, vz)`, calculamos trajetória:

**Horizontal (sem gravidade):**
$$x(t) = x_0 + v_x \times t$$
$$y(t) = y_0 + v_y \times t$$

**Vertical (com gravidade):**
$$z(t) = z_0 + v_z \times t - \frac{1}{2} \times g \times t^2$$

**Onde:**
- $g = 9.81 \, m/s^2$ (gravidade da Terra)
- $t$ = tempo futuro

### Ponto de Impacto

Para saber **quando** o objeto atinge altura do robô:

$$0.5 = z_0 + v_z \times t - \frac{1}{2} \times g \times t^2$$

Resolvendo com **Bhaskara**:

$$t = \frac{-v_z + \sqrt{v_z^2 + 2 \times g \times (z_0 - 0.5)}}{g}$$

Então calculamos **onde** estará:

$$x_{land} = x_0 + v_x \times t$$
$$y_{land} = y_0 + v_y \times t$$
$$z_{land} = 0.5 \, m$$ (altura do robô)

**Resultado:** `(x_land, y_land, 0.5)` = ponto de aterrissagem! 🎯

## 💻 Implementação

### Estrutura do Código

```
detection/modules/
├── spatial.py        # Conversão 2D→3D, cálculo de distância
├── physics.py        # Velocidade, trajetória, predição
├── vision.py         # Visualização 3D (Matplotlib)
└── run_prediction.py # Orquestração do sistema
```

### Fluxo de Processamento

```python
# 1. Detecção YOLO (2D)
results = model(frame)
bbox = results[0].boxes[0].xyxy  # (x1, y1, x2, y2)

# 2. Conversão para 3D (spatial.py)
position_3d = pixel_to_3d(bbox, class_id, focal_length)
# Retorna: (x, y, z) em metros

# 3. Tracking e Velocidade (physics.py)
velocity_3d = calculate_velocity(position_history)
# Retorna: (vx, vy, vz) em m/s

# 4. Predição de Trajetória (physics.py)
landing_point = predict_landing(position_3d, velocity_3d, robot_height)
# Retorna: (x_land, y_land, z_land, t_land)

# 5. Comando ao Robô
robot_command = landing_point_to_vector(landing_point)
# Retorna: (vx_normalized, vy_normalized)
```

## ⚙️ Configuração

### Parâmetros Importantes

```python
# detection/modules/config.py

# Dimensões reais dos objetos (CALIBRAR!)
OBJECT_DIMENSIONS = {
    0: 0.17,  # can - 17cm altura
    1: 0.10   # paper - 10cm diâmetro amassado
}

# Focal length (pixels) - depende da câmera
FOCAL_LENGTH = 500  # Típico para webcam 640x640

# Altura do robô (metros)
ROBOT_HEIGHT = 0.5  # 50cm

# Gravidade
GRAVITY = 9.81  # Terra (m/s²)

# Tracking
MIN_TRACKING_FRAMES = 5  # Mínimo de frames para calcular velocidade
MAX_HISTORY = 20         # Máximo de posições no histórico
```

### Calibração da Focal Length

A focal length depende da **câmera e resolução**:

```python
# Método 1: Medir distância conhecida
# 1. Coloque objeto a 1 metro da câmera
# 2. Detecte e veja largura em pixels
# 3. Calcule: f = (width_pixels * distance) / real_width

# Exemplo:
# Latinha (6cm) a 1m aparece com 30 pixels
f = (30 * 1.0) / 0.06 = 500 pixels

# Método 2: Usar especificações da câmera
# f = (sensor_width_pixels * focal_length_mm) / sensor_width_mm
```

### Calibração das Dimensões

**Importante:** Meça os objetos reais!

```python
# Latinha típica 350ml
OBJECT_DIMENSIONS[0] = 0.12  # 12cm altura

# Papel amassado (medir diâmetro típico)
OBJECT_DIMENSIONS[1] = 0.08  # 8cm
```

**Dica:** Objetos maiores = detecção de distância mais precisa!

## 📊 Precisão do Sistema

### Fatores que Afetam Precisão

1. **Focal Length calibrada** ⭐
   - Erro de 10% na focal = Erro de 10% na distância
   
2. **Dimensões reais corretas** ⭐
   - Erro de 5cm = Erro de ~20cm na distância (a 1m)

3. **Resolução da câmera**
   - 640x640: Precisão média
   - 1280x1280: Alta precisão
   - 416x416: Baixa precisão

4. **Tamanho do objeto na imagem**
   - >50 pixels: Boa precisão
   - 20-50 pixels: Média precisão
   - <20 pixels: Baixa precisão

5. **Estabilidade da detecção**
   - Confidence >0.5: Estável
   - Confidence <0.3: Instável (velocidade ruidosa)

### Erro Típico

Com boa calibração:

| Distância | Erro Típico |
|-----------|-------------|
| 0.5m | ±5cm |
| 1.0m | ±10cm |
| 2.0m | ±20cm |
| 3.0m | ±40cm |

## 🎨 Visualização 3D

### Ativar Modo Desenvolvedor

Pressione **D** durante execução para ver:

```
┌─────────────────────────────────────┐
│  Visualização 3D                    │
│                                     │
│    Z ↑                              │
│      |     🔵 Objeto atual          │
│      |    /                         │
│      |   /  Trajetória prevista    │
│      |  /                           │
│      | /                            │
│      |/                             │
│      o────→ Y (Profundidade)        │
│     /                               │
│    ↙ X (Esq/Dir)                   │
│                                     │
│  🟢 Ponto de impacto previsto      │
└─────────────────────────────────────┘
```

### Elementos da Visualização

- **🔵 Ponto azul**: Posição atual do objeto
- **📈 Linha azul**: Trajetória prevista (parábola)
- **🟢 Ponto verde**: Ponto de aterrissagem previsto
- **Eixos**: X (esquerda/direita), Y (profundidade), Z (altura)
- **Grid**: Escala em metros

## 🤖 Comando ao Robô

### Conversão: Landing Point → Vetor de Movimento

```python
# Ponto de aterrissagem previsto
landing_point = (x_land, y_land, z_land)

# Posição atual do robô (assumindo no centro)
robot_position = (0, 0, robot_height)

# Vetor de movimento = landing - robot
vx = landing_point[0] - robot_position[0]
vy = landing_point[1] - robot_position[1]

# Normalizar para [-1, 1]
max_distance = 2.0  # Alcance máximo do robô (metros)
vx_normalized = clamp(vx / max_distance, -1, 1)
vy_normalized = clamp(vy / max_distance, -1, 1)

# Enviar ao robô
command = f"V:{vy_normalized:.3f},{vx_normalized:.3f}"
# Exemplo: "V:0.500,0.300"
```

### Protocolo WebSocket

```
Formato: V:vy,vx

Exemplos:
"V:0.500,0.000"  → Frente (50%)
"V:-0.500,0.000" → Trás (50%)
"V:0.000,0.500"  → Direita (50%)
"V:0.000,-0.500" → Esquerda (50%)
"V:0.707,0.707"  → Diagonal (frente-direita)
"V:0.000,0.000"  → Parar
```

Ver [CarrinhoMovimentacao.md](CarrinhoMovimentacao.md) para detalhes do controle Mecanum.

## 🧪 Testar o Sistema

### Teste de Calibração

```bash
cd detection
python main.py

# Pressione D para ativar visualização 3D
# Coloque objeto a distâncias conhecidas e compare
```

### Validar Distância

```python
# Adicione prints em spatial.py
print(f"Distância calculada: {distance:.2f}m")
print(f"Posição 3D: x={x:.2f}, y={y:.2f}, z={z:.2f}")

# Compare com medição real usando trena!
```

### Validar Velocidade

```python
# Adicione prints em physics.py
print(f"Velocidade: vx={vx:.2f}, vy={vy:.2f}, vz={vz:.2f} m/s")

# Velocidade vertical deve ser negativa se caindo
# vz ≈ -2 m/s é típico para objetos em queda livre
```

## 💡 Dicas de Uso

1. **Calibre primeiro** - Focal length e dimensões são críticas
2. **Boa iluminação** - Detecção estável = velocidade precisa
3. **Objetos grandes** - Mais fácil de detectar distância correta
4. **Múltiplos frames** - MIN_TRACKING_FRAMES = 5+ para precisão
5. **Visualização 3D** - Use tecla D para debug visual
6. **Teste gradual** - Objetos parados → lentos → rápidos

## 📚 Referências

- [PHYSICS.md](PHYSICS.md) - Detalhes da física aplicada
- [Pinhole Camera Model](https://en.wikipedia.org/wiki/Pinhole_camera_model)
- [Projectile Motion](https://en.wikipedia.org/wiki/Projectile_motion)

---

## 🎯 Resumo

Este sistema **NÃO usa área de pixels** simplista. Utiliza:

1. ✅ **Geometria de câmera** (pinhole model)
2. ✅ **Dimensões reais** dos objetos
3. ✅ **Física completa** (gravidade, trajetória)
4. ✅ **Tracking temporal** (velocidade via regressão)
5. ✅ **Predição 3D** (onde vai cair)

É um sistema **robusto e preciso** quando bem calibrado! 🚀
