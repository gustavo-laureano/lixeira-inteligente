# 🌐 Interface Web - Controle Virtual

Interface web para controle do robô e teste de latência.

## 📁 Estrutura

```
web/
├── index.html    # Interface de controle WebSocket
└── README.md     # Este arquivo
```

## 🚀 Uso

### Opção 1: Abrir diretamente no navegador

1. Inicie o servidor API:
```bash
cd ../api
python api_server.py
```

2. Abra `index.html` no navegador:
   - Duplo clique no arquivo, ou
   - Arraste para o navegador, ou
   - Use `file:///caminho/para/web/index.html`

3. Configure a URI do servidor (ex: `ws://192.168.2.106:8000/ws/controller`)
4. Clique em "Conectar"

### Opção 2: Servir via servidor HTTP (recomendado)

Para melhor compatibilidade, sirva a pasta via servidor HTTP:

```bash
# Python 3
cd web
python -m http.server 8080

# Ou Node.js
npx http-server -p 8080
```

Acesse: `http://localhost:8080/index.html`

## 🎮 Controles

### Botões de Movimento
- **W / Frente**: Move para frente
- **S / Trás**: Move para trás
- **A / Esquerda**: Move para esquerda
- **D / Direita**: Move para direita
- **Q / Girar Esq**: Rotação esquerda
- **E / Girar Dir**: Rotação direita
- **X / Parar**: Para o robô

### Comportamento
- **Mousedown/Touch**: Envia comando de movimento
- **Mouseup/Touch**: Envia automaticamente `x` (parar)
- Simula controle estilo joystick em tempo real

### Teste de Latência
- Clique em "📊 Testar Latência API" para medir RTT

## 🔧 Configuração

Edite a URI do servidor no campo de input:
- Local: `ws://localhost:8000/ws/controller`
- Rede local: `ws://192.168.1.100:8000/ws/controller`

A interface converte automaticamente `http://` para `ws://`.

## 📱 Compatibilidade

- ✅ Desktop (Chrome, Firefox, Edge)
- ✅ Mobile (iOS Safari, Chrome Mobile)
- ✅ Suporte a touch events

