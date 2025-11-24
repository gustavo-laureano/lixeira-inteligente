# 🚀 Guia de Otimização para PC

Este documento contém dicas e técnicas para otimizar a performance do sistema YOLO customizado rodando em PC/Laptop.

## 📊 Performance Esperada

### PC com GPU NVIDIA (CUDA)
- **YOLOv8n (640x640)**: 60-120 FPS
- **Com visualização 3D**: 40-80 FPS
- **Latência**: <20ms

### PC sem GPU (CPU apenas)
- **YOLOv8n (640x640)**: 15-30 FPS
- **Com visualização 3D**: 10-20 FPS
- **Latência**: 30-60ms

### Laptop (CPU integrada)
- **YOLOv8n (640x640)**: 10-20 FPS
- **Com visualização 3D**: 8-15 FPS
- **Latência**: 50-100ms

## ⚙️ Otimizações de Software

### 1. Usar GPU (NVIDIA CUDA)

#### Instalar CUDA e cuDNN

**Windows:**
```powershell
# 1. Instalar CUDA Toolkit 11.8+
# Download: https://developer.nvidia.com/cuda-downloads

# 2. Instalar cuDNN
# Download: https://developer.nvidia.com/cudnn

# 3. Instalar PyTorch com CUDA
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
```

**Linux:**
```bash
# CUDA + PyTorch
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
```

#### Verificar GPU

```python
import torch

print(f"CUDA disponível: {torch.cuda.is_available()}")
print(f"GPU: {torch.cuda.get_device_name(0)}")
print(f"Versão CUDA: {torch.version.cuda}")
```

**Resultado esperado:**
```
CUDA disponível: True
GPU: NVIDIA GeForce RTX 3060
Versão CUDA: 11.8
```

### 2. Resolução da Câmera

Resolução impacta **diretamente** o desempenho:

```python
# config.py

# ⚡ RÁPIDO - Menos preciso
CAMERA_WIDTH = 416
CAMERA_HEIGHT = 416

# ⚖️ BALANCEADO - Recomendado ⭐
CAMERA_WIDTH = 640
CAMERA_HEIGHT = 640

# 🎯 PRECISO - Mais lento
CAMERA_WIDTH = 1280
CAMERA_HEIGHT = 1280
```

**Trade-off:**
- 416x416: +50% FPS, -20% precisão
- 640x640: Performance balanceada
- 1280x1280: -40% FPS, +15% precisão

### 3. Confidence Threshold

```python
# config.py

# Menos detecções = mais rápido
CONFIDENCE_THRESHOLD = 0.25  # Conservador

# Balanceado ⭐
CONFIDENCE_THRESHOLD = 0.15  # Recomendado

# Mais detecções = mais lento
CONFIDENCE_THRESHOLD = 0.05  # Agressivo
```

### 4. FPS da Câmera

```python
# config.py

# Baixo FPS - Economiza CPU
CAMERA_FPS = 30

# Médio FPS - Balanceado ⭐
CAMERA_FPS = 60

# Alto FPS - Usa mais CPU
CAMERA_FPS = 120
```

**Nota:** FPS alto não melhora detecção necessariamente!

### 5. Modelo YOLO

```python
# config.py

# Nano - Mais rápido ⭐
MODEL_PATH = "detection/models/below-trash-v2.pt"  # YOLOv8n base

# Small - Mais preciso, mais lento
# (Você precisaria retreinar com yolov8s.pt)
```

### 6. Desativar Visualização 3D

A janela 3D consome recursos:

```python
# config.py

# Desativa visualização por padrão (use D para ativar)
DEFAULT_DEV_MODE = False
```

Ou pressione **D** durante execução para alternar.

### 7. Otimizar Tracking

```python
# config.py

# Mínimo de frames para calcular velocidade
MIN_TRACKING_FRAMES = 3  # Rápido, menos preciso
# MIN_TRACKING_FRAMES = 5  # Balanceado ⭐
# MIN_TRACKING_FRAMES = 10  # Lento, mais preciso

# Buffer de histórico
MAX_HISTORY = 15  # Reduz memória
```

### 8. Threads da Câmera

```python
# camera_manager.py

# Usar threads para captura não-bloqueante
self.use_threading = True  # ⭐ Ativado por padrão
```

## 🔧 Otimizações de Hardware

### 1. Câmera USB

**Recomendações:**
- Use porta **USB 3.0** (azul)
- Evite hubs USB
- Use cabo curto (<1m)
- Câmera com compressão H.264 (reduz largura de banda)

### 2. GPU

**Performance por GPU:**
| GPU | FPS (640x640) | Custo/Performance |
|-----|---------------|-------------------|
| RTX 4090 | 200+ | Excelente |
| RTX 3060 | 80-120 | Excelente ⭐ |
| GTX 1660 | 50-70 | Boa |
| GTX 1050 Ti | 30-40 | Aceitável |
| Integrada Intel | 10-15 | Ruim |

### 3. CPU

**Recomendações (se sem GPU):**
- Intel i5/i7 (8ª geração+)
- AMD Ryzen 5/7 (3000+)
- Mínimo 4 cores / 8 threads

### 4. RAM

- **Mínimo:** 8GB
- **Recomendado:** 16GB ⭐
- **Ideal:** 32GB

**Dica:** Feche programas desnecessários!

## 📈 Monitoramento

### 1. FPS em Tempo Real

O sistema já exibe FPS no terminal:

```
🎯 Detectado can (0.85) - Tracking ID: 1 [FPS: 45.2]
```

### 2. GPU Utilization (NVIDIA)

**Windows/Linux:**
```bash
# Terminal separado
nvidia-smi -l 1
```

**Resultado esperado:**
```
GPU  Name        Util  Memory-Usage
  0  RTX 3060    85%   2000MiB / 12288MiB
```

### 3. CPU e Memória

**Windows (PowerShell):**
```powershell
Get-Process python | Format-Table CPU, WS -AutoSize
```

**Linux:**
```bash
htop
# Ou
top -p $(pgrep -f "main.py")
```

## ⚡ Otimizações Avançadas

### 1. TensorRT (NVIDIA apenas)

Converta modelo para TensorRT (5x mais rápido):

```python
from ultralytics import YOLO

model = YOLO('detection/models/below-trash-v2.pt')

# Exportar para TensorRT
model.export(format='engine', device=0)

# Usar modelo otimizado
model = YOLO('detection/models/below-trash-v2.engine')
```

**Ganho:** 2-5x FPS

### 2. ONNX Runtime

Alternativa para CPU/GPU:

```bash
pip install onnxruntime-gpu  # ou onnxruntime para CPU
```

```python
# Exportar
model.export(format='onnx')

# Usar
model = YOLO('detection/models/below-trash-v2.onnx')
```

### 3. Half Precision (FP16)

Reduz uso de memória e aumenta FPS:

```python
# Inferência
results = model(frame, half=True)  # FP16 ao invés de FP32
```

**Ganho:** 1.5-2x FPS (GPU apenas)

### 4. Batch Processing (Não recomendado para tempo real)

Se processar múltiplas imagens:

```python
# Lista de frames
frames = [frame1, frame2, frame3]

# Batch inference (mais rápido que loop)
results = model(frames)
```

### 5. Compilação com PyTorch 2.0

```bash
pip install --upgrade torch
```

```python
# main.py
import torch

# Compilar modelo (primeira execução demora)
model = torch.compile(model)
```

**Ganho:** 10-30% FPS

## 🎯 Configuração Recomendada

### Para PC com GPU ⭐

```python
# config.py

# Câmera
CAMERA_WIDTH = 640
CAMERA_HEIGHT = 640
CAMERA_FPS = 60

# Modelo
MODEL_PATH = "detection/models/below-trash-v2.pt"
CONFIDENCE_THRESHOLD = 0.15

# Performance
MIN_TRACKING_FRAMES = 5
MAX_HISTORY = 20
DEFAULT_DEV_MODE = True  # Pode ativar visualização

# Física
ROBOT_HEIGHT = 0.5
GRAVITY = 9.81
```

**FPS esperado:** 60-100

### Para PC sem GPU

```python
# config.py

# Câmera - Reduzir resolução
CAMERA_WIDTH = 416
CAMERA_HEIGHT = 416
CAMERA_FPS = 30

# Modelo
MODEL_PATH = "detection/models/below-trash-v2.pt"
CONFIDENCE_THRESHOLD = 0.20  # Mais alto para reduzir processamento

# Performance
MIN_TRACKING_FRAMES = 3  # Menos frames
MAX_HISTORY = 10
DEFAULT_DEV_MODE = False  # Desativar 3D

# Física
ROBOT_HEIGHT = 0.5
GRAVITY = 9.81
```

**FPS esperado:** 15-25

### Para Laptop

```python
# config.py

# Câmera - Resolução mínima
CAMERA_WIDTH = 416
CAMERA_HEIGHT = 416
CAMERA_FPS = 30

# Modelo
MODEL_PATH = "detection/models/below-trash-v1.pt"  # Modelo mais leve
CONFIDENCE_THRESHOLD = 0.25

# Performance
MIN_TRACKING_FRAMES = 3
MAX_HISTORY = 10
DEFAULT_DEV_MODE = False

# Física
ROBOT_HEIGHT = 0.5
GRAVITY = 9.81
```

**FPS esperado:** 10-20

## 🔍 Diagnóstico de Performance

### Identificar Gargalo

Execute com profile:

```python
# main.py
import cProfile
import pstats

profiler = cProfile.Profile()
profiler.enable()

# Seu código aqui
main()

profiler.disable()
stats = pstats.Stats(profiler)
stats.sort_stats('cumulative')
stats.print_stats(20)  # Top 20 funções
```

**Gargalos comuns:**
1. **`model.predict`** - Inferência YOLO (normal)
2. **`cv2.imshow`** - Visualização (desative se lento)
3. **`matplotlib`** - Plotagem 3D (pressione D para desativar)

### Benchmark

```bash
cd detection

# Teste de 100 frames
python -m timeit -n 1 -r 1 "import main; main.main()"
```

## 💡 Dicas Finais

1. **GPU é game-changer** - Investe em GPU se possível
2. **Feche programas** - Chrome usa muita RAM
3. **Resolução baixa primeiro** - Aumente gradualmente
4. **Desative 3D** - Use só quando necessário
5. **Monitore temperatura** - GPU com throttling = FPS baixo
6. **Drivers atualizados** - NVIDIA drivers sempre atualizados
7. **Cabo USB 3.0** - Câmera em USB 2.0 gargala
8. **Iluminação boa** - Reduz ruído, melhora detecção

## 📊 Tabela de Comparação

| Configuração | GPU | Resolução | FPS | Precisão | Uso |
|-------------|-----|-----------|-----|----------|-----|
| Ultra | RTX 3060+ | 1280x1280 | 40 | Excelente | Demonstração |
| Alta | RTX 3060 | 640x640 | 80 | Alta | Produção ⭐ |
| Média | GTX 1050 | 640x640 | 35 | Alta | Produção |
| Baixa | CPU i7 | 416x416 | 20 | Média | Testes |
| Mínima | CPU i5 | 416x416 | 12 | Média | Básico |

## 🐛 Problemas Comuns

### FPS muito baixo

1. **Verifique GPU:**
   ```python
   import torch
   print(torch.cuda.is_available())
   ```

2. **Reduza resolução:**
   ```python
   CAMERA_WIDTH = 416
   CAMERA_HEIGHT = 416
   ```

3. **Desative visualização 3D** (tecla D)

4. **Feche programas pesados**

### Alto uso de memória

1. **Reduza histórico:**
   ```python
   MAX_HISTORY = 10
   ```

2. **Use FP16:**
   ```python
   results = model(frame, half=True)
   ```

3. **Feche aplicações**

### Detecções imprecisas

1. **Aumente resolução:**
   ```python
   CAMERA_WIDTH = 640
   CAMERA_HEIGHT = 640
   ```

2. **Diminua confidence:**
   ```python
   CONFIDENCE_THRESHOLD = 0.10
   ```

3. **Melhore iluminação**

---

**Resumo**: GPU NVIDIA é altamente recomendada. Comece com configuração balanceada (640x640) e ajuste conforme performance. Monitore FPS e ajuste gradualmente! ⚡
