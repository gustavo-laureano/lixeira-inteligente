# 📏 Sistema de Detecção de Distância

## 🎯 Como Funciona

O sistema agora detecta a **distância do objeto** baseado no **tamanho aparente** (área em pixels) na imagem.

### Princípio Básico

```
Objeto LONGE     →  Aparece PEQUENO  →  Área em pixels BAIXA
Objeto PERTO     →  Aparece GRANDE   →  Área em pixels ALTA
Objeto MUITO PERTO → Aparece ENORME  →  Área em pixels MUITO ALTA
```

## 📊 Zonas de Distância

O sistema divide em **4 zonas** baseadas na área do objeto:

| Zona | Área (pixels²) | Descrição | Ação do Arduino |
|------|---------------|-----------|----------------|
| 🔴 **VERY_CLOSE** | > 50.000 | Muito perto! | ⬅️ **RECUA** |
| 🟡 **CLOSE** | 20.000 - 50.000 | Alcançou objeto | ⏸️ **PARA** |
| 🟢 **MEDIUM** | 10.000 - 20.000 | Distância média | 🐢 Avança devagar |
| 🔵 **FAR** | < 10.000 | Longe | 🚀 Avança rápido |

## 🔧 Configuração

### config.yaml

```yaml
detection:
  distance_thresholds:
    very_close: 50000   # > 50k = MUITO PERTO (recuar)
    close: 20000        # > 20k = PERTO (parar)
    medium: 10000       # > 10k = MÉDIO (devagar)
    # < 10k = LONGE (rápido)
```

**Ajuste estes valores conforme:**
- Tamanho dos objetos que você detecta
- Resolução da câmera (640x480)
- Distância desejada da lixeira ao objeto
- Campo de visão da câmera

## 📐 Cálculo da Área

```python
# detect.py
x1, y1, x2, y2 = box.xyxy[0]  # Coordenadas do retângulo
area = (x2 - x1) * (y2 - y1)  # Área em pixels²

# Exemplo: Garrafa de 100x300 pixels = 30.000 pixels²
```

### Exemplos Visuais

#### Garrafa Longe (FAR)
```
┌──────────────────────┐
│                      │
│                      │
│       [🍾]          │  ← Pequena (5.000 pixels²)
│                      │
│                      │
└──────────────────────┘
Comando: BOTTLE:CENTER:FAR
Ação: Avança RÁPIDO
```

#### Garrafa Média Distância (MEDIUM)
```
┌──────────────────────┐
│                      │
│        ┌──┐         │
│        │🍾│         │  ← Média (15.000 pixels²)
│        └──┘         │
│                      │
└──────────────────────┘
Comando: BOTTLE:CENTER:MEDIUM
Ação: Avança DEVAGAR
```

#### Garrafa Perto (CLOSE)
```
┌──────────────────────┐
│      ┌────┐         │
│      │    │         │
│      │ 🍾 │         │  ← Grande (30.000 pixels²)
│      │    │         │
│      └────┘         │
└──────────────────────┘
Comando: BOTTLE:CENTER:CLOSE
Ação: PARA (alcançou)
```

#### Garrafa Muito Perto (VERY_CLOSE)
```
┌──────────────────────┐
│  ┌────────────────┐ │
│  │                │ │
│  │      🍾       │ │  ← Enorme (60.000 pixels²)
│  │                │ │
│  └────────────────┘ │
└──────────────────────┘
Comando: BOTTLE:CENTER:VERY_CLOSE
Ação: RECUA ⬅️
```

## 🤖 Comportamento do Arduino

### Fluxograma de Decisão

```
Comando recebido: BOTTLE:LEFT:MEDIUM
         ↓
    Parse comando
         ↓
    distance = "MEDIUM"
    position = "LEFT"
         ↓
    if (distance == "VERY_CLOSE")
         ├─ Não
         ↓
    if (distance == "CLOSE")
         ├─ Não
         ↓
    if (distance == "MEDIUM")  ← ✅ SIM!
         ↓
    if (position == "LEFT")    ← ✅ SIM!
         ↓
    turnLeft()
    moveForwardSlow()
         ↓
    stopMotors()
    Serial.println("OK")
```

### Código Arduino

```cpp
void processCommand(String cmd) {
  // Parse
  String distance = parseDistance(cmd);
  String position = parsePosition(cmd);
  
  // Decisão baseada na distância
  if (distance == "VERY_CLOSE") {
    // ⬅️ RECUAR - Passou do ponto!
    Serial.println("RECUANDO!");
    moveBackward(500);  // Recua por 500ms
    
  } else if (distance == "CLOSE") {
    // ⏸️ PARAR - Alcançou o objeto!
    Serial.println("PARADO - Objeto alcançado");
    stopMotors();
    // Aqui você pode acionar garra, tampa, etc
    
  } else if (distance == "MEDIUM") {
    // 🐢 APROXIMAR DEVAGAR
    Serial.println("Aproximando devagar...");
    
    // Ajusta direção primeiro
    if (position == "LEFT") {
      turnLeft();
    } else if (position == "RIGHT") {
      turnRight();
    }
    
    // Avança devagar
    moveForward(300, 100);  // 300ms, velocidade 100
    
  } else if (distance == "FAR") {
    // 🚀 AVANÇAR RÁPIDO
    Serial.println("Avançando rápido!");
    
    // Ajusta direção
    if (position == "LEFT") {
      turnLeft();
    } else if (position == "RIGHT") {
      turnRight();
    }
    
    // Avança rápido
    moveForward(800, 200);  // 800ms, velocidade 200
  }
  
  stopMotors();
  Serial.println("OK");
}
```

## 🎯 Sequência Completa de Aproximação

### Cenário: Garrafa detectada à esquerda, longe

```
1️⃣ Detecção inicial
   └─> BOTTLE:LEFT:FAR (área: 5.000 px²)
   └─> Arduino: Vira esquerda + Avança RÁPIDO

2️⃣ Após ~1 segundo (Arduino moveu)
   └─> BOTTLE:CENTER:FAR (área: 8.000 px²)
   └─> Arduino: Avança RÁPIDO (já está centralizado)

3️⃣ Após mais ~1 segundo
   └─> BOTTLE:CENTER:MEDIUM (área: 15.000 px²)
   └─> Arduino: Avança DEVAGAR (está ficando perto)

4️⃣ Após mais ~0.5 segundo
   └─> BOTTLE:CENTER:CLOSE (área: 30.000 px²)
   └─> Arduino: PARA! ✅ (alcançou o objeto)

5️⃣ Se continuar avançando...
   └─> BOTTLE:CENTER:VERY_CLOSE (área: 60.000 px²)
   └─> Arduino: RECUA! ⬅️ (passou do ponto)
```

## ⚙️ Calibração

### Como Ajustar os Thresholds

1. **Execute o sistema** apontando para um objeto
2. **Observe os logs** para ver a área detectada:
   ```
   Detectado: bottle (conf: 0.85, área: 25000, pos: CENTER, dist: CLOSE)
   ```

3. **Ajuste config.yaml** baseado nos valores reais:

```yaml
# Se objetos são detectados como CLOSE muito cedo:
distance_thresholds:
  very_close: 60000  # Aumenta threshold
  close: 30000       # Aumenta threshold
  medium: 15000      # Aumenta threshold

# Se objetos são detectados como FAR muito tempo:
distance_thresholds:
  very_close: 40000  # Diminui threshold
  close: 15000       # Diminui threshold
  medium: 7000       # Diminui threshold
```

### Teste de Calibração

```bash
# Coloque um objeto em diferentes distâncias e veja os logs
docker-compose logs -f | grep "área:"

# Exemplos de output:
# 3 metros: área: 3000   → FAR ✅
# 2 metros: área: 8000   → FAR ✅
# 1 metro:  área: 15000  → MEDIUM ✅
# 50cm:     área: 35000  → CLOSE ✅
# 20cm:     área: 65000  → VERY_CLOSE ✅
```

## 🔍 Debug

### Ver Áreas Detectadas em Tempo Real

```python
# Adicione no detect.py se quiser debug visual
logger.info(f"ÁREA: {area:.0f} → DISTÂNCIA: {distance}")
```

### Testar Manualmente

```bash
# Enviar comandos de teste direto pro Arduino
python3 test_serial.py /dev/ttyUSB0 9600

# Digite:
BOTTLE:CENTER:FAR
BOTTLE:CENTER:MEDIUM
BOTTLE:CENTER:CLOSE
BOTTLE:CENTER:VERY_CLOSE
```

## 💡 Dicas

1. **Iluminação importa**: Baixa luz = detecção ruim = área imprecisa
2. **Fundo limpo**: Fundo confuso pode aumentar área detectada
3. **Objetos similares**: Garrafas grandes vs pequenas têm áreas diferentes na mesma distância
4. **Ajuste por tipo**: Você pode ter thresholds diferentes para cada classe:

```python
# Ideia: Thresholds personalizados (não implementado)
thresholds = {
    'bottle': {'very_close': 60000, 'close': 30000, 'medium': 15000},
    'cup': {'very_close': 40000, 'close': 20000, 'medium': 10000},
}
```

## 🎓 Conceitos

### Por que Área e não Distância Real?

**YOLO não mede distância diretamente!** Ele só detecta objetos em imagens 2D.

Para distância REAL você precisaria:
- **Sensor ultrassônico** (HC-SR04)
- **Câmera estéreo** (duas câmeras)
- **Sensor de profundidade** (Intel RealSense, Kinect)

Mas para a lixeira, **área em pixels é suficiente**! É rápido, simples e funciona bem.

---

**Resumo**: Sistema agora detecta 4 níveis de distância baseado na área do objeto. Arduino pode RECUAR quando muito perto, PARAR quando alcançou, ou AVANÇAR (devagar/rápido) quando longe. ✅
