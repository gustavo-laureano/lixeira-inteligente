# 🚀 Guia de Otimização para Raspberry Pi

Este documento contém dicas e técnicas para otimizar a performance do sistema YOLO no Raspberry Pi.

## 📊 Performance Esperada

### Raspberry Pi 4 (4GB)
- **YOLOv8n (640x480)**: 10-15 FPS
- **YOLOv8n (320x240)**: 20-25 FPS
- **YOLOv8s (640x480)**: 3-5 FPS

### Raspberry Pi 3
- **YOLOv8n (640x480)**: 5-8 FPS
- **YOLOv8n (320x240)**: 12-15 FPS

## ⚙️ Otimizações de Software

### 1. Resolução da Câmera

Menor resolução = mais FPS:

```yaml
# config.yaml
camera:
  resolution: [320, 240]  # QVGA - muito rápido
  # resolution: [640, 480]  # VGA - balanceado
  # resolution: [1280, 720]  # HD - muito lento!
```

### 2. Frame Skip

Processe apenas alguns frames:

```yaml
# config.yaml
performance:
  frame_skip: 2  # Processa 1 a cada 2 frames (2x mais rápido)
```

No código Python:
```python
frame_count = 0
while True:
    ret, frame = camera.read()
    frame_count += 1
    
    # Só processa a cada X frames
    if frame_count % 2 != 0:
        continue
    
    results = model(frame)
```

### 3. Confidence Threshold

Maior confidence = menos processamento:

```yaml
# config.yaml
yolo:
  confidence: 0.6  # Aumente para reduzir falsos positivos
```

### 4. Área Mínima

Ignore objetos pequenos:

```yaml
# config.yaml
detection:
  min_area: 2000  # Aumente para ignorar objetos menores
```

### 5. Modelo YOLO

Use o modelo mais leve:

```yaml
# config.yaml
yolo:
  model: "yolov8n.pt"  # ✅ RECOMENDADO - mais rápido
  # model: "yolov8s.pt"  # Mais lento
```

### 6. Reduzir Classes

Detecte apenas o necessário:

```yaml
# config.yaml
detection:
  classes: ["bottle"]  # Apenas 1 classe = mais rápido
  # Quanto menos classes, mais rápido
```

### 7. Buffer da Câmera

```python
camera.set(cv2.CAP_PROP_BUFFERSIZE, 1)  # Buffer mínimo
```

## 🐳 Otimizações do Docker

### 1. Limitar Recursos

Evite que Docker use toda a memória:

```yaml
# docker-compose.yml
deploy:
  resources:
    limits:
      cpus: '3.0'
      memory: 1G
```


## 📈 Benchmark e Monitoramento

### Verificar FPS

```bash
docker-compose logs -f | grep "FPS:"
```

### Monitorar Recursos

```bash
# CPU, RAM, Temperatura
watch -n 1 'vcgencmd measure_temp && free -h && top -bn1 | head -20'

# Docker stats
docker stats lixeira-inteligente
```


## 🎯 Configuração Recomendada

Para melhor balanço performance/precisão:

```yaml
# config.yaml
camera:
  resolution: [640, 480]
  fps: 30
  device: 0

yolo:
  model: "yolov8n.pt"
  confidence: 0.5
  iou: 0.45

detection:
  classes: ["bottle", "cup", "can"]
  min_area: 1500

performance:
  frame_skip: 1
  num_threads: 4
```

## 🔋 Redução de Latência

Para decisões mais rápidas:

1. **Priorize processamento sobre qualidade**:
   - Resolução baixa (320x240)
   - Frame skip (2-3)
   - Confiança média (0.4-0.5)

2. **Reduza overhead de comunicação**:
   - Comandos simples para Arduino
   - Baudrate alto (115200)
   - Sem delay desnecessário

3. **Otimize código Arduino**:
   - Parse rápido de comandos
   - Ações não-bloqueantes
   - Evite Serial.print excessivo



## 🧪 Teste de Performance

Execute o benchmark:

```bash
# Teste com resolução padrão
time python3 detect.py

# Monitore em tempo real
watch -n 1 docker-compose logs --tail=10
```

## 📊 Tabela de Comparação

| Configuração | FPS (Pi 4) | Latência | Precisão |
|-------------|------------|----------|----------|
| 320x240 + skip=2 | ~30 | Baixa | Média |
| 640x480 + skip=1 | ~12 | Média | Alta |
| 640x480 + skip=2 | ~20 | Baixa | Alta |
| 1280x720 + skip=1 | ~3 | Alta | Muito Alta |

## 💡 Dicas Finais

1. **Comece simples**: Use configuração padrão e ajuste gradualmente
2. **Meça sempre**: Use logs para verificar FPS real
3. **Temperatura**: Monitore constantemente - é o fator #1
4. **Trade-offs**: Mais velocidade = menos precisão (encontre seu balanço)
5. **Teste real**: Performance de laboratório ≠ performance real

## 🐛 Problemas Comuns

### FPS muito baixo
- Verifique temperatura (throttling)
- Reduza resolução
- Aumente frame_skip
- Use modelo nano

### Alto uso de memória
- Reduza buffer da câmera
- Limite recursos do Docker
- Feche aplicações desnecessárias

### Detecções imprecisas
- Aumente resolução
- Reduza frame_skip
- Ajuste confiança
- Melhore iluminação

---

**Lembre-se**: O Raspberry Pi não é um computador de alta performance. Ajuste suas expectativas e otimize para seu caso de uso específico!
