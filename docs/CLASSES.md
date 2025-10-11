# 🎯 Classes YOLO - Guia Completo

## 📌 Resumo Executivo

O modelo `yolov8n.pt` vem **pré-treinado** com o dataset COCO e detecta **80 classes** diferentes sem necessidade de treinar nada. Basta baixar e usar!

## ✅ Como Funciona

### 1. Download Automático
```python
from ultralytics import YOLO

# Na primeira execução, baixa automaticamente (~6MB)
model = YOLO('yolov8n.pt')

# Pronto para usar!
results = model('imagem.jpg')
```

### 2. Detecção Imediata
```python
# Detecta automaticamente os 80 objetos do COCO
results = model(frame, conf=0.5)

# Acessa detecções
for box in results[0].boxes:
    class_id = int(box.cls[0])
    class_name = model.names[class_id]
    confidence = float(box.conf[0])
    print(f"Detectado: {class_name} ({confidence:.2%})")
```

## 🎯 Classes COCO (80 objetos)

### 👤 Pessoas e Animais (10)
```
person, bird, cat, dog, horse, sheep, cow, elephant, bear, zebra, giraffe
```

### 🚗 Veículos (8)
```
bicycle, car, motorcycle, airplane, bus, train, truck, boat
```

### 🚦 Objetos Urbanos (5)
```
traffic light, fire hydrant, stop sign, parking meter, bench
```

### 🍽️ Utensílios e Recipientes (12) ⭐ **MAIS RELEVANTE PARA LIXEIRA**
```
bottle       - Garrafas PET, vidro (também detecta latas cilíndricas)
wine glass   - Taças, cálices
cup          - Copos, xícaras, canecas
fork         - Garfos
knife        - Facas
spoon        - Colheres
bowl         - Tigelas, bowls, bacias
```

### 🍎 Alimentos (11) ⭐ **ÚTIL PARA LIXEIRA**
```
banana, apple, sandwich, orange, broccoli, carrot, hot dog,
pizza, donut, cake
```

### 🎒 Acessórios (10)
```
backpack, umbrella, handbag, tie, suitcase, frisbee, skis,
snowboard, sports ball, kite
```

### 🎾 Esportes (4)
```
baseball bat, baseball glove, skateboard, surfboard, tennis racket
```

### 🏠 Móveis (6)
```
chair, couch, potted plant, bed, dining table, toilet
```

### 💻 Eletrônicos (10)
```
tv, laptop, mouse, remote, keyboard, cell phone, microwave,
oven, toaster, sink, refrigerator
```

### 📚 Objetos Diversos (4)
```
book, clock, vase, scissors, teddy bear, hair drier, toothbrush
```

## ⚠️ Classes NÃO Disponíveis

### Latas (can/soda can) ❌
**O dataset COCO NÃO inclui "can" (lata de refrigerante/cerveja)**

**Soluções:**

1. **Usar "bottle"** (mais simples):
   - Muitas latas cilíndricas são detectadas como `bottle`
   - Funciona para maioria dos casos

2. **Treinar modelo customizado**:
   ```python
   # Crie seu dataset de latas
   model = YOLO('yolov8n.pt')
   model.train(data='latas_dataset.yaml', epochs=50)
   ```

3. **Adicionar sensor de metal**:
   ```python
   if detected_class == "bottle" and metal_sensor.detect():
       object_type = "metal_can"
   else:
       object_type = "plastic_bottle"
   ```

### Outros Objetos Comuns Não Disponíveis:
- Papel / Papelão
- Sacola plástica (apenas `handbag` existe)
- Embalagens genéricas
- Isopor
- Vidro quebrado

## 🔧 Configuração para Lixeira

### Config Recomendado
```yaml
# config.yaml
detection:
  classes:
    - "bottle"      # Garrafas e latas cilíndricas
    - "cup"         # Copos
    - "bowl"        # Tigelas
    - "fork"        # Opcional: talheres
    - "knife"       # Opcional: talheres
    - "spoon"       # Opcional: talheres
```

### Config Minimalista (Melhor Performance)
```yaml
detection:
  classes:
    - "bottle"      # Apenas garrafas
    - "cup"         # Apenas copos
```

## 🧪 Testar Classes

### Script de Teste
```bash
# Ver todas as 80 classes disponíveis
python3 test_yolo_classes.py

# Opções:
# 1. Testar com câmera ao vivo
# 2. Testar com imagem
# 3. Apenas listar classes
```

### Teste Rápido em Python
```python
from ultralytics import YOLO

model = YOLO('yolov8n.pt')

# Ver todas as classes
print("Classes disponíveis:")
for idx, name in model.names.items():
    print(f"  {idx:2d} - {name}")

# Testar detecção
results = model('sua_imagem.jpg', conf=0.5)
results[0].show()  # Mostra imagem com detecções
```

## 📊 Precisão por Classe

Classes com melhor detecção no COCO:
- ✅ **Excelente** (>90%): person, car, chair, bottle, cup
- 🟢 **Boa** (70-90%): fork, knife, spoon, bowl, apple, banana
- 🟡 **Média** (50-70%): wine glass, orange, sandwich
- 🔴 **Variável** (<50%): objetos pequenos, mal iluminados

## 💡 Dicas de Uso

### 1. Filtre Apenas Classes Necessárias
```python
# Mais rápido: detecta tudo mas só processa o que interessa
target_classes = ['bottle', 'cup', 'bowl']

for box in results[0].boxes:
    class_name = model.names[int(box.cls[0])]
    if class_name in target_classes:
        # Processa apenas estas classes
        process(box)
```

### 2. Ajuste Confidence por Classe
```python
# Algumas classes precisam confidence maior
confidence_thresholds = {
    'bottle': 0.5,   # Garrafas: confiança média
    'cup': 0.6,      # Copos: mais exigente
    'bowl': 0.4,     # Tigelas: menos exigente
}

for box in results[0].boxes:
    class_name = model.names[int(box.cls[0])]
    confidence = float(box.conf[0])
    min_conf = confidence_thresholds.get(class_name, 0.5)
    
    if confidence >= min_conf:
        process(box)
```

### 3. Combine com Tamanho
```python
# Ignore objetos muito pequenos (ruído)
min_areas = {
    'bottle': 2000,  # Garrafas devem ser grandes
    'cup': 1000,     # Copos podem ser menores
    'spoon': 500,    # Colheres são pequenas
}

x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
area = (x2 - x1) * (y2 - y1)

if area >= min_areas.get(class_name, 1000):
    process(box)
```


## 🔗 Recursos

- **Ultralytics Docs**: https://docs.ultralytics.com
- **COCO Dataset**: https://cocodataset.org
- **Modelos pré-treinados**: https://github.com/ultralytics/assets/releases


  git config --global user.email "gustavolaureanodealmeida@gmail.com"
  git config --global user.name "Gustavo Laureano"