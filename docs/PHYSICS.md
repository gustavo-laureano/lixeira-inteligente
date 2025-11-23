# 🎯 Física da Predição de Trajetória

Este documento explica **em linguagem simples** como o sistema prevê onde objetos em queda vão atingir o chão.

## 📖 Índice

- [Analogia Simples](#analogia-simples)
- [Conceitos Físicos](#conceitos-físicos)
- [Fórmulas Principais](#fórmulas-principais)
- [Como Funciona na Prática](#como-funciona-na-prática)
- [Exemplo Concreto](#exemplo-concreto)
- [Limitações](#limitações)

---

## 🎈 Analogia Simples

Imagine que você joga uma bola para cima. Você quer saber:
1. **Onde ela vai cair no chão?**
2. **Qual caminho ela vai fazer no ar?**

Este código faz exatamente isso, mas usando a câmera para "ver" objetos em movimento (como papeis amassados ou latinhas).

---

## 📐 Conceitos Físicos

### 1. **Posição 3D (x, y, z)**

Qualquer objeto no espaço tem 3 coordenadas:

- **x**: esquerda(-) / direita(+) ← →
- **y**: trás(-) / frente(+) ↑ ↓  
- **z**: altura do chão ⬆️

**Exemplo:** Um papel a 1 metro de altura, 0.5m à direita da câmera, e 2m de distância está em:
```
posição = [0.5, 2.0, 1.0]
```

### 2. **Velocidade (vx, vy, vz)**

É **quanto o objeto se move por segundo** em cada direção.

- Se `vz = -2 m/s`, o objeto está **caindo** 2 metros por segundo
- Se `vx = 1 m/s`, está se movendo 1 metro/s **para a direita**
- Se `vy = 0 m/s`, está **parado** na profundidade

**Exemplo:** 
```
velocidade = [0.0, 0.2, -1.5]
```
Significa: parado horizontalmente, indo 0.2m/s para frente, caindo a 1.5m/s

### 3. **Gravidade (g = 9.81 m/s²)**

É a força que **puxa tudo para baixo** na Terra.

- Todo objeto cai acelerando **9.81 m/s** a cada segundo
- Por isso objetos caem **cada vez mais rápido**
- É uma constante universal (na Terra)

**Analogia:** É como um carro acelerando - começa devagar e vai ficando cada vez mais rápido.

---

## 🧮 Fórmulas Principais

### 1. Equação do Movimento Vertical (Queda Livre)

```
z(t) = z₀ + vz·t - ½·g·t²
```

**Onde:**
- `z(t)` = altura no tempo t
- `z₀` = altura inicial (onde começou)
- `vz` = velocidade vertical inicial
- `g` = gravidade (9.81)
- `t` = tempo decorrido

**Explicação:** A altura diminui com o tempo devido à gravidade (parte `-½·g·t²`)

---

### 2. Equação do Movimento Horizontal

```
x(t) = x₀ + vx·t
y(t) = y₀ + vy·t
```

**Explicação:** Na horizontal **não há gravidade**, então o objeto mantém velocidade constante.

---

### 3. Fórmula de Bhaskara (achar quando atinge o chão)

Para descobrir o t, precisamos organizar a equação do Movimento Uniformemente Variado (MUV) para que ela fique igual a zero. Vamos jogar tudo para um lado só:

$$-\frac{1}{2} g t^2 + v_z t + (z_0 - h_{robo}) = 0$$

**Onde:**
* `t`: Tempo até o impacto (o que queremos descobrir)
* `g`: Gravidade (9.81 m/s²)
* `vz`: Velocidade vertical atual
* `z0`: Altura atual do objeto
* `h_robo`: Altura alvo (onde o robô vai pegar)

```
t = (-b ± √(b² - 4ac)) / (2a)
```

**Onde:**
- `a = -½·g = -4.905` (efeito da gravidade)
- `b = vz` (velocidade vertical)
- `c = z₀ - altura_do_robô` (diferença de altura)

**Explicação:** Resolve quando `z(t) = altura_do_robô` (momento do impacto).

Esta é a mesma fórmula que você aprende na escola para resolver `ax² + bx + c = 0`!


Bhaskara sempre dá duas respostas (t1 e t2). Na física, isso acontece porque, teoricamente, o objeto poderia passar pela altura do robô duas vezes:

 - Subindo (quando você joga ele para o alto).

 - Descendo (depois que ele parou de subir e começou a cair).

O código usa max(t1, t2) para pegar o tempo futuro (o momento em que ele vai cair na mão do robô), ignorando o passado ou o momento do lançamento

---
## 🔍 Como Funciona na Prática

### Passo 1: RASTREAMENTO 📹

A câmera vê o objeto em várias posições ao longo do tempo:

```
t=0.0s: objeto em (0.5, 1.0, 2.0)
t=0.1s: objeto em (0.6, 1.1, 1.9)
t=0.2s: objeto em (0.7, 1.2, 1.7)
```

### Passo 2: CÁLCULO DE VELOCIDADE 📊

Compara posições anteriores usando **regressão linear** (traça uma linha de melhor ajuste):

```
Velocidade = (posição_final - posição_inicial) / tempo_decorrido
```

**Exemplo:** Se em 0.2s o objeto caiu de z=2.0 para z=1.7:
```
vz = (1.7 - 2.0) / 0.2 = -1.5 m/s (caindo)
```

### Passo 3: PREDIÇÃO 🎯

Usa as fórmulas acima para calcular:
- **QUANDO** vai atingir a altura do robô (tempo de impacto)
- **ONDE** estará nesse momento (ponto de aterrissagem)
- **TODO O CAMINHO** até lá (trajetória completa)

---

## 💡 Exemplo Concreto

### Situação:

Um **papel amassado** é jogado para cima:

```
📍 Posição atual: x=0, y=1.0m, z=2.5m (2.5m de altura)
🏃 Velocidade: vx=0, vy=0, vz=-1.0 m/s (caindo a 1 m/s)
🤖 Altura do robô: 0.5m
🌍 Gravidade: 9.81 m/s²
```

### Cálculo do Tempo de Impacto:

Queremos descobrir quando o papel vai atingir z = 0.5m (altura do robô).

**Equação:**
```
z(t) = 2.5 + (-1.0)·t - ½·(9.81)·t² = 0.5
2.5 - 1.0·t - 4.905·t² = 0.5
-4.905·t² - 1.0·t + 2.0 = 0
```

**Bhaskara:**
```
a = -4.905
b = -1.0
c = 2.0

delta = b² - 4ac = 1 + 39.24 = 40.24

t = (1.0 + √40.24) / 9.81 = (1.0 + 6.34) / 9.81 = 0.75s
```

### Posição de Impacto:

Agora que sabemos que vai levar **0.75 segundos**, calculamos onde vai estar:

```
x = 0 + 0·0.75 = 0m (não se moveu horizontalmente)
y = 1.0 + 0·0.75 = 1.0m (manteve a distância)
z = 0.5m (altura do robô)
```

### 🎉 Resultado Final:

```
O papel vai cair em (0, 1.0, 0.5) depois de 0.75 segundos!
```

O robô deve se posicionar em **x=0, y=1.0m** para pegar o papel! 🗑️

---

## 📈 Visualizando a Trajetória

O sistema gera vários pontos ao longo do caminho (a cada 0.05s por padrão):

```python
t=0.00s → (0.0, 1.0, 2.500)  # Agora
t=0.15s → (0.0, 1.0, 2.240)  # ⬇️
t=0.30s → (0.0, 1.0, 1.859)  # ⬇️⬇️
t=0.45s → (0.0, 1.0, 1.357)  # ⬇️⬇️⬇️
t=0.60s → (0.0, 1.0, 0.734)  # ⬇️⬇️⬇️⬇️
t=0.75s → (0.0, 1.0, 0.500)  # 💥 IMPACTO!
```

**Note:** O objeto cai cada vez **mais rápido** devido à aceleração da gravidade!

Esta lista de pontos forma uma **parábola** (curva característica de objetos em queda livre).

---

## ⚠️ Limitações

### 1. **Assume que não há vento**
O movimento é perfeitamente parabólico. Na vida real, vento pode desviar o objeto.

### 2. **Ignora resistência do ar**
Objetos muito leves (como penas) caem mais devagar do que a física prevê.

### 3. **Precisa de pelo menos 3 medições**
O sistema precisa ver o objeto em 3 momentos diferentes para calcular velocidade.

### 4. **Quanto mais medições, mais preciso**
Com 10 medições é muito mais preciso do que com 3.

### 5. **Assume velocidade constante na horizontal**
Se o objeto estiver girando ou desviando, a precisão cai.

---


## 📚 Referências

- [ Prevendo Trajetória da Bola de Basquete com Visão Computacional e Estatística ](https://youtu.be/HvKLK_SeKns?si=uEVrX0h8lg8RP8LYo)


