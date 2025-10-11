# 🚀 Quick Start Guide

Guia rápido para colocar a Lixeira Inteligente funcionando em 15 minutos!

## 📋 Pré-requisitos

- Raspberry Pi 3/4/5 com Raspberry Pi OS
- Câmera USB ou CSI
- Arduino conectado via USB
- Conexão com internet

## ⚡ Instalação Rápida

### 1. Instalar Docker (5 min)

```bash
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER
sudo apt install docker-compose -y
sudo reboot
```

### 2. Clonar e Configurar (2 min)

```bash
cd ~
git clone https://github.com/gustavo-laureano/lixeira-inteligente.git
cd lixeira-inteligente
mkdir -p logs models data
```

### 3. Identificar Dispositivos (2 min)

```bash
# Câmera
ls -l /dev/video*
# Anote o device (geralmente /dev/video0)

# Arduino
ls -l /dev/ttyUSB* /dev/ttyACM*
# Anote a porta (geralmente /dev/ttyUSB0 ou /dev/ttyACM0)
```

### 4. Configurar (1 min)

Edite `config.yaml`:

```bash
nano config.yaml
```

Ajuste apenas estas linhas:

```yaml
camera:
  device: 0  # Seu device de câmera

serial:
  port: "/dev/ttyUSB0"  # Sua porta serial
  baudrate: 9600         # Igual ao Arduino
```

Salve: `Ctrl+X`, `Y`, `Enter`

Edite `docker-compose.yml`:

```bash
nano docker-compose.yml
```

Ajuste os devices:

```yaml
devices:
  - /dev/video0:/dev/video0    # Seu device de câmera
  - /dev/ttyUSB0:/dev/ttyUSB0  # Sua porta serial
```

Salve: `Ctrl+X`, `Y`, `Enter`

### 5. Build e Executar (5 min)

```bash
# Build (demora um pouco na primeira vez)
docker-compose build

# Iniciar
docker-compose up -d

# Ver logs
docker-compose logs -f
```

Pronto! 🎉 O sistema está rodando!

## 🎯 Comandos Úteis

```bash
# Ver logs
docker-compose logs -f

# Parar
docker-compose down

# Reiniciar
docker-compose restart

# Atualizar código
git pull
docker-compose up -d --build
```

## 🧪 Testar Componentes

```bash
# Testar câmera
python3 test_camera.py

# Testar Arduino
python3 test_serial.py /dev/ttyUSB0 9600
```

## 📱 Arduino - Código Mínimo

Copie para o Arduino IDE:

```cpp
void setup() {
  Serial.begin(9600);
  Serial.println("Arduino pronto!");
}

void loop() {
  if (Serial.available() > 0) {
    String cmd = Serial.readStringUntil('\n');
    Serial.println("Recebido: " + cmd);
    
    // Parse: OBJETO:POSICAO:DISTANCIA
    int firstColon = cmd.indexOf(':');
    int secondColon = cmd.indexOf(':', firstColon + 1);
    String distance = cmd.substring(secondColon + 1);
    String position = cmd.substring(firstColon + 1, secondColon);
    
    // Lógica baseada na distância
    if (distance == "VERY_CLOSE") {
      moveBackward();  // ⬅️ RECUA se muito perto
    } else if (distance == "CLOSE") {
      stopMotors();    // ⏸️ PARA se alcançou
    } else if (distance == "MEDIUM") {
      moveForwardSlow();  // 🐢 Devagar
    } else {
      moveForwardFast();  // 🚀 Rápido
    }
    
    Serial.println("OK");
  }
}
```

## ⚙️ Configuração Recomendada

Para melhor performance no Raspberry Pi 4:

```yaml
# config.yaml
camera:
  resolution: [640, 480]
  fps: 30

yolo:
  model: "yolov8n.pt"
  confidence: 0.5

detection:
  classes: ["bottle", "cup", "can"]
  min_area: 1000

performance:
  frame_skip: 1
```

## 🐛 Problemas Comuns

### Câmera não funciona
```bash
sudo chmod 666 /dev/video0
sudo usermod -aG video $USER
```

### Arduino não responde
```bash
sudo usermod -aG dialout $USER
sudo chmod 666 /dev/ttyUSB0
# Logout e login novamente
```

### Performance ruim
```bash
# Verificar temperatura
vcgencmd measure_temp
# Se > 80°C, adicione refrigeração!

# Reduzir resolução
nano config.yaml
# Mude: resolution: [320, 240]
```

### Docker build falha
```bash
# Limpar e tentar novamente
docker system prune -a
docker-compose build --no-cache
```

## 📚 Documentação Completa

- [README.md](README.md) - Documentação completa
- [CLASSES.md](CLASSES.md) - **Classes detectadas pelo YOLO (80 objetos)**
- [OPTIMIZATION.md](OPTIMIZATION.md) - Otimizações de performance
- [TROUBLESHOOTING.md](TROUBLESHOOTING.md) - Resolução de problemas
- [arduino_example.ino](arduino_example.ino) - Código Arduino completo

## 🎓 Próximos Passos

1. ✅ Sistema funcionando básico
2. 📝 Customize `config.yaml` para seu caso
3. 🤖 Implemente lógica no Arduino
4. ⚡ Otimize para melhor performance
5. 🎯 Ajuste detecção para objetos específicos

## 💡 Dicas Importantes

- **Refrigeração é ESSENCIAL** - Use ventoinha e dissipadores
- **Fonte adequada** - Use fonte oficial 5V 3A
- **Iluminação** - Ambiente bem iluminado = melhor detecção
- **Teste gradualmente** - Comece simples, adicione complexidade depois
- **Monitore logs** - `docker-compose logs -f` é seu amigo

## 🆘 Precisa de Ajuda?

1. Veja [TROUBLESHOOTING.md](TROUBLESHOOTING.md)
2. Execute testes: `python3 test_camera.py` e `python3 test_serial.py`
3. Verifique logs: `docker-compose logs`
4. Abra issue no GitHub com logs e detalhes

---

**Tempo total**: ~15 minutos (excluindo download do modelo YOLO)

**FPS esperado**: 10-15 FPS no Raspberry Pi 4 (640x480)

Boa sorte! 🚀
