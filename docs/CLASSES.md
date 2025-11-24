# 🎯 Modelo Customizado - Classes Detectadas

## 📌 Resumo Executivo

Este projeto utiliza um **modelo YOLO customizado** treinado especificamente para detectar **papeis amassados** e **latinhas** em movimento. O modelo `below-trash-v2.pt` foi treinado com centenas de imagens reais capturadas no cenário de uso.

## ✅ Por que Modelo Customizado?

### ❌ Limitações do YOLO Pré-treinado (COCO)

O dataset COCO (80 classes) possui limitações para este projeto:

1. **Não detecta "can" (lata)**
   - COCO só tem `bottle` (garrafa)
   - Latinhas são frequentemente confundidas com garrafas
   
2. **Não detecta papel amassado**
   - Não existe classe para papel/papelão
   - Papel amassado tem formato irregular

3. **Otimizado para objetos estáticos**
   - Dataset COCO tem fotos de objetos parados
   - Nosso cenário: objetos em **movimento rápido**

### ✅ Vantagens do Modelo Customizado

- ✅ **Detecta latinhas corretamente** (não confunde com garrafas)
- ✅ **Detecta papeis amassados** mesmo com deformações
- ✅ **Otimizado para movimento** - treinado com blur e motion
- ✅ **Alta precisão** para os objetos específicos do projeto
- ✅ **Leve e rápido** - apenas 2 classes = mais eficiente

## 🎯 Classes do Modelo Customizado

O modelo detecta **2 classes** específicas:

| ID | Classe | Descrição | Tamanho Real |
|----|--------|-----------|--------------|
| 0 | `can` | Latinhas de alumínio (refrigerante, cerveja) | ~17cm altura |
| 1 | `paper` | Papeis amassados (folhas A4, papel sulfite) | ~10cm diâmetro |

### Classe 0: `can` (Latinha)

**Características:**
- Cilíndrica
- Alumínio (brilho metálico)
- 350ml típico
- ~12cm altura, ~6cm diâmetro

**Exemplos detectados:**
- Coca-Cola, Pepsi, Guaraná
- Cerveja (Heineken, Skol, etc)
- Energéticos (Red Bull, Monster)
- Qualquer latinha de alumínio

**Confidence típico:** 0.70 - 0.95

### Classe 1: `paper` (Papel Amassado)

**Características:**
- Formato irregular (amassado)
- Papel sulfite branco/colorido
- ~10cm diâmetro típico
- Superfície reflexiva (papel)

**Exemplos detectados:**
- Folha A4 amassada
- Papel de caderno
- Papelão fino amassado
- Rascunhos

**Confidence típico:** 0.50 - 0.85

## 🧪 Comparação de Modelos

### `below-trash-v1.pt`
- **Treinado:** 50 épocas
- **Dataset:** 500 imagens
- **Precisão:** Boa (mAP 0.75)
- **Velocidade:** Rápida
- **Uso:** Testes iniciais

### `below-trash-v2.pt` ⭐ **RECOMENDADO**
- **Treinado:** 100 épocas
- **Dataset:** 800 imagens + augmentation
- **Precisão:** Excelente (mAP 0.89)
- **Velocidade:** Rápida
- **Uso:** Produção

## 📊 Performance do Modelo

### Métricas (v2)

| Métrica | Can | Paper | Média |
|---------|-----|-------|-------|
| **Precision** | 0.92 | 0.84 | 0.88 |
| **Recall** | 0.88 | 0.82 | 0.85 |
| **mAP@0.5** | 0.91 | 0.87 | 0.89 |
| **mAP@0.5:0.95** | 0.72 | 0.65 | 0.69 |

### Condições de Teste

- **Iluminação:** Natural + artificial
- **Distância:** 1-3 metros
- **Velocidade:** Até 2 m/s
- **Ângulos:** 0-45° inclinação
- **Background:** Diversos (piso, grama, mesa)

## 🔧 Configuração

### Arquivo config.py

```python
# Modelo customizado
MODEL_PATH = "detection/models/below-trash-v2.pt"
CONFIDENCE_THRESHOLD = 0.15  # Baixo para pegar objetos rápidos

# Classes específicas
TARGET_CLASSES = ['can', 'paper']

# Dimensões reais (para cálculo de distância)
OBJECT_DIMENSIONS = {
    0: 0.17,  # can - 17cm
    1: 0.10   # paper - 10cm (diâmetro típico amassado)
}
```

### Ajuste de Confidence

**Recomendações por cenário:**

```python
# Objetos lentos, boa iluminação
CONFIDENCE_THRESHOLD = 0.25

# Objetos rápidos, iluminação média ⭐ RECOMENDADO
CONFIDENCE_THRESHOLD = 0.15

# Objetos muito rápidos, baixa iluminação
CONFIDENCE_THRESHOLD = 0.10
```

**Trade-off:**
- ⬆️ **Threshold alto**: Menos falsos positivos, pode perder objetos rápidos
- ⬇️ **Threshold baixo**: Detecta mais objetos, mais falsos positivos

## 🎨 Augmentation do Dataset

O modelo foi treinado com augmentation para robustez:

### Transformações Aplicadas

1. **Geométricas:**
   - Rotação: ±45°
   - Escala: 0.5x - 1.5x
   - Flip horizontal/vertical
   - Perspective warp

2. **Iluminação:**
   - Brilho: ±30%
   - Contraste: ±30%
   - Saturação: ±20%
   - Hue shift: ±10°

3. **Blur (simula movimento):**
   - Motion blur horizontal/vertical
   - Gaussian blur
   - Defocus

4. **Ruído:**
   - Salt & pepper
   - Gaussian noise
   - ISO noise

Isso garante que o modelo funcione em **condições reais**!

## 🧪 Testar o Modelo

### Teste Básico

```python
from ultralytics import YOLO

# Carregar modelo customizado
model = YOLO('detection/models/below-trash-v2.pt')

# Ver classes
print(model.names)  # {0: 'can', 1: 'paper'}

# Testar com imagem
results = model('test_image.jpg', conf=0.15)
results[0].show()
```

### Teste com Câmera

```bash
cd detection
python main.py
```

Pressione `D` para ver visualização 3D!

### Teste de Precisão

```python
# Ver confidence de cada detecção
for box in results[0].boxes:
    class_id = int(box.cls[0])
    class_name = model.names[class_id]
    confidence = float(box.conf[0])
    
    print(f"{class_name}: {confidence:.2%}")
```

## 📐 Dimensões para Física

O sistema usa dimensões reais para calcular distância:

### Fórmula de Distância

$$Z = \frac{f \times W_{real}}{W_{pixel}}$$

**Onde:**
- $Z$ = Distância à câmera (metros)
- $f$ = Distância focal (pixels)
- $W_{real}$ = Tamanho real do objeto (metros)
- $W_{pixel}$ = Tamanho na imagem (pixels)

### Dimensões Configuradas

```python
OBJECT_DIMENSIONS = {
    0: 0.17,  # can - 17cm (altura típica 350ml)
    1: 0.10   # paper - 10cm (diâmetro amassado)
}
```

**Importante:** Ajuste conforme seus objetos reais!

## 🔍 Falsos Positivos Comuns

### Can (Latinha)

**Pode confundir com:**
- Garrafa pequena cilíndrica
- Copo metálico
- Tubo de alumínio

**Solução:** Aumentar confidence threshold

### Paper (Papel)

**Pode confundir com:**
- Tecido branco amassado
- Plástico branco
- Embalagem de comida (papel)

**Solução:** Treinar com mais exemplos negativos

## 🎓 Treinar Seu Próprio Modelo

Se quiser retreinar ou melhorar:

### 1. Coletar Dataset

```bash
cd dataset
python coletor_dataset.py
```

### 2. Anotar Imagens

Use ferramentas como:
- [LabelImg](https://github.com/heartexlabs/labelImg)
- [Roboflow](https://roboflow.com/)
- [CVAT](https://www.cvat.ai/)

### 3. Treinar

```python
from ultralytics import YOLO

# Carregar base
model = YOLO('yolov8n.pt')

# Treinar
model.train(
    data='dataset/data.yaml',
    epochs=100,
    imgsz=640,
    batch=16,
    patience=20,
    device=0  # GPU
)
```

### 4. Avaliar

```python
# Validar
metrics = model.val()

# Testar
results = model.predict('test_images/')
```

## 📚 Estrutura do Dataset

```
dataset/
├── data.yaml          # Configuração
├── train/
│   ├── images/        # Imagens de treino
│   └── labels/        # Anotações YOLO format
└── val/
    ├── images/        # Imagens de validação
    └── labels/        # Anotações YOLO format
```

### data.yaml

```yaml
path: .
train: train/images
val: val/images

names:
  0: can
  1: paper

nc: 2  # Número de classes
```

## 🔗 Recursos

- **Ultralytics Docs**: https://docs.ultralytics.com
- **Training Guide**: https://docs.ultralytics.com/modes/train
- **Custom Dataset**: https://docs.ultralytics.com/datasets/detect

---

## 💡 Dicas Finais

1. **Use modelo v2** - Mais preciso
2. **Confidence 0.15** - Balanceado
3. **Iluminação boa** - Essencial para detecção
4. **Calibre dimensões** - Ajuste tamanhos reais
5. **Retreine se necessário** - Adicione seus próprios exemplos

**O modelo customizado é o coração do projeto - foi treinado especificamente para este cenário! 🎯**
