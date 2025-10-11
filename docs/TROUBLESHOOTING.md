# 🔧 Guia de Troubleshooting

Soluções para problemas comuns ao executar o sistema YOLO no Raspberry Pi.

## 📹 Problemas com Câmera

### ❌ Câmera não detectada

**Sintomas:**
```
Erro: Não foi possível abrir a câmera
```

**Soluções:**

1. **Verificar se câmera está conectada:**
   ```bash
   ls -l /dev/video*
   v4l2-ctl --list-devices
   ```

2. **Para câmera USB:**
   ```bash
   # Reconectar USB
   sudo rmmod uvcvideo
   sudo modprobe uvcvideo
   ```

3. **Para câmera CSI (Raspberry Pi Camera):**
   ```bash
   # Habilitar em raspi-config
   sudo raspi-config
   # Interface Options -> Camera -> Enable
   
   # Verificar
   vcgencmd get_camera
   # Deve retornar: supported=1 detected=1
   ```

4. **Permissões:**
   ```bash
   sudo chmod 666 /dev/video0
   sudo usermod -aG video $USER
   ```

5. **Testar câmera:**
   ```bash
   # USB
   fswebcam test.jpg
   
   # CSI
   raspistill -o test.jpg
   ```

### ❌ Imagem preta ou congelada

**Soluções:**

1. **Aumentar timeout:**
   ```python
   camera = cv2.VideoCapture(0)
   camera.set(cv2.CAP_PROP_BUFFERSIZE, 1)
   time.sleep(2)  # Aguarda câmera inicializar
   ```

2. **Verificar iluminação**

3. **Testar outra resolução:**
   ```yaml
   camera:
     resolution: [320, 240]
   ```

### ❌ FPS muito baixo

Ver [OPTIMIZATION.md](OPTIMIZATION.md) para detalhes completos.

**Verificações rápidas:**
```bash
# Temperatura
vcgencmd measure_temp
# Se > 80°C, adicione refrigeração!

# Throttling
vcgencmd get_throttled
# Se != 0x0, há problemas de alimentação/temperatura
```

## 🔌 Problemas com Serial (Arduino)

### ❌ Porta serial não encontrada

**Sintomas:**
```
FileNotFoundError: [Errno 2] No such file or directory: '/dev/ttyUSB0'
```

**Soluções:**

1. **Identificar porta correta:**
   ```bash
   # Desconecte Arduino
   ls /dev/tty*
   
   # Conecte Arduino
   ls /dev/tty*
   
   # A nova porta é o Arduino (geralmente ttyUSB0 ou ttyACM0)
   ```

2. **Ajustar config.yaml:**
   ```yaml
   serial:
     port: "/dev/ttyACM0"  # ou ttyUSB0
   ```

3. **Permissões:**
   ```bash
   sudo usermod -aG dialout $USER
   sudo chmod 666 /dev/ttyUSB0
   # Logout/login necessário
   ```

### ❌ Sem comunicação com Arduino

**Sintomas:**
- Comandos enviados mas Arduino não responde
- Serial timeout

**Soluções:**

1. **Verificar baudrate:**
   ```yaml
   # config.yaml
   serial:
     baudrate: 9600  # DEVE SER IGUAL ao Arduino
   ```
   
   ```cpp
   // Arduino
   Serial.begin(9600);  // MESMO valor
   ```

2. **Testar comunicação:**
   ```bash
   python3 test_serial.py /dev/ttyUSB0 9600
   ```

3. **Monitor Serial Arduino:**
   ```bash
   sudo apt install screen
   screen /dev/ttyUSB0 9600
   # Ctrl+A, K para sair
   ```

4. **Verificar cabo USB:**
   - Use cabo USB com dados (não só alimentação)
   - Teste outro cabo

5. **Reset Arduino:**
   ```bash
   # Desconectar e reconectar
   # Ou via software:
   python3 -c "import serial; s=serial.Serial('/dev/ttyUSB0',9600); s.setDTR(False); s.setDTR(True); s.close()"
   ```

## 🐳 Problemas com Docker

### ❌ Build falha

**Sintomas:**
```
ERROR: failed to solve: ...
```

**Soluções:**

1. **Limpar cache:**
   ```bash
   docker system prune -a
   docker-compose build --no-cache
   ```

2. **Verificar espaço em disco:**
   ```bash
   df -h
   # Precisa de pelo menos 5GB livres
   ```

3. **Aumentar swap temporariamente:**
   ```bash
   sudo dphys-swapfile swapoff
   sudo nano /etc/dphys-swapfile
   # CONF_SWAPSIZE=2048
   sudo dphys-swapfile setup
   sudo dphys-swapfile swapon
   ```

4. **Build em etapas:**
   ```bash
   docker build --target base -t lixeira:base .
   docker build -t lixeira:latest .
   ```

### ❌ Container não inicia

**Sintomas:**
```
Error response from daemon: ...
```

**Soluções:**

1. **Ver logs completos:**
   ```bash
   docker-compose logs
   docker logs lixeira-inteligente
   ```

2. **Verificar dispositivos:**
   ```bash
   # Câmera
   ls -l /dev/video0
   
   # Serial
   ls -l /dev/ttyUSB0
   ```

3. **Ajustar docker-compose.yml:**
   ```yaml
   devices:
     - /dev/video0:/dev/video0
     # Comente se não tiver Arduino conectado:
     # - /dev/ttyUSB0:/dev/ttyUSB0
   ```

4. **Modo interativo para debug:**
   ```bash
   docker run -it --rm \
     --device=/dev/video0 \
     --privileged \
     lixeira-inteligente /bin/bash
   ```

### ❌ Erro de permissão

**Sintomas:**
```
Permission denied: '/dev/video0'
```

**Soluções:**

1. **Usar modo privileged:**
   ```yaml
   # docker-compose.yml
   privileged: true
   ```

2. **Ajustar permissões:**
   ```bash
   sudo chmod 666 /dev/video0
   sudo chmod 666 /dev/ttyUSB0
   ```

## 🧠 Problemas com YOLO

### ❌ Modelo não baixa

**Sintomas:**
```
Error downloading model...
```

**Soluções:**

1. **Baixar manualmente:**
   ```bash
   cd models
   wget https://github.com/ultralytics/assets/releases/download/v0.0.0/yolov8n.pt
   ```

2. **Verificar conexão internet:**
   ```bash
   ping google.com
   ```

3. **Usar modelo local:**
   ```python
   # Se já tiver o modelo
   model = YOLO('models/yolov8n.pt')
   ```

### ❌ Detecções ruins

**Soluções:**

1. **Ajustar confiança:**
   ```yaml
   yolo:
     confidence: 0.3  # Diminua para mais detecções
     # confidence: 0.7  # Aumente para menos falsos positivos
   ```

2. **Melhorar iluminação:**
   - Adicione luz ambiente
   - Evite contra-luz
   - Use iluminação uniforme

3. **Aumentar resolução:**
   ```yaml
   camera:
     resolution: [640, 480]  # ou maior
   ```

4. **Testar com imagens:**
   ```python
   from ultralytics import YOLO
   model = YOLO('yolov8n.pt')
   results = model('test.jpg')
   results[0].show()
   ```

### ❌ Memória insuficiente

**Sintomas:**
```
RuntimeError: out of memory
```

**Soluções:**

1. **Reduzir resolução:**
   ```yaml
   camera:
     resolution: [320, 240]
   ```

2. **Limitar recursos Docker:**
   ```yaml
   deploy:
     resources:
       limits:
         memory: 512M
   ```

3. **Usar modelo menor:**
   ```yaml
   yolo:
     model: "yolov8n.pt"  # O MENOR disponível
   ```

4. **Fechar outros programas:**
   ```bash
   sudo systemctl stop bluetooth
   sudo systemctl stop cups
   ```

## 🔥 Problemas de Performance

### ❌ Sistema lento / lag

**Verificações:**

1. **Temperatura:**
   ```bash
   vcgencmd measure_temp
   # Se > 80°C, ADICIONE REFRIGERAÇÃO!
   ```

2. **Throttling:**
   ```bash
   vcgencmd get_throttled
   
   # 0x0 = OK
   # 0x50000 = Throttling passado
   # 0x50005 = Throttling ativo + passado
   ```

3. **Alimentação:**
   ```bash
   vcgencmd get_throttled
   # Problemas = alimentação fraca
   # Use fonte oficial 5V 3A
   ```

4. **Memória:**
   ```bash
   free -h
   # Se swap está sendo usado, problema de memória
   ```

**Soluções:** Ver [OPTIMIZATION.md](OPTIMIZATION.md)

### ❌ Alta latência nas decisões

**Soluções:**

1. **Frame skip agressivo:**
   ```yaml
   performance:
     frame_skip: 3
   ```

2. **Resolução mínima:**
   ```yaml
   camera:
     resolution: [320, 240]
   ```

3. **Baudrate maior:**
   ```yaml
   serial:
     baudrate: 115200
   ```

4. **Otimizar código Arduino:**
   - Evite delays
   - Parse rápido de comandos
   - Use interrupções

## 💾 Problemas de Sistema

### ❌ SD Card cheio

```bash
# Verificar espaço
df -h

# Limpar Docker
docker system prune -a

# Limpar logs
sudo journalctl --vacuum-size=100M
rm -rf logs/*

# Limpar APT cache
sudo apt clean
```

### ❌ Sistema instável / crashes

**Soluções:**

1. **Verificar logs do sistema:**
   ```bash
   dmesg | tail -50
   sudo journalctl -xe
   ```

2. **Verificar memória:**
   ```bash
   vcgencmd get_mem arm && vcgencmd get_mem gpu
   ```

3. **Verificar alimentação:**
   - Use fonte oficial 5V 3A
   - Evite hubs USB sem alimentação
   - Verifique cabo de alimentação

4. **Watchdog automático:**
   ```bash
   sudo apt install watchdog
   sudo systemctl enable watchdog
   ```

## 🔍 Debug Avançado

### Modo verbose

```yaml
# config.yaml
logging:
  level: "DEBUG"
```

### Executar sem Docker

```bash
python3 detect.py
# Vê erros diretamente
```

### Logs detalhados Docker

```bash
docker-compose logs -f --tail=100
```

### Testar componentes isoladamente

```bash
# Apenas câmera
python3 test_camera.py

# Apenas serial
python3 test_serial.py

# Apenas YOLO
python3 -c "from ultralytics import YOLO; model = YOLO('yolov8n.pt'); print('OK')"
```

## 📞 Checklist de Verificação

Antes de pedir ajuda, verifique:

- [ ] Raspberry Pi alimentado corretamente (5V 3A)
- [ ] Temperatura < 80°C
- [ ] Câmera conectada e reconhecida
- [ ] Arduino conectado e respondendo
- [ ] Docker instalado e funcionando
- [ ] Espaço suficiente em disco (>2GB)
- [ ] Permissões corretas (dialout, video)
- [ ] Logs verificados
- [ ] Configurações corretas em config.yaml

## 🆘 Ainda com problemas?

1. **Veja os logs:**
   ```bash
   docker-compose logs > debug.log
   cat debug.log
   ```

2. **Informações do sistema:**
   ```bash
   cat /proc/cpuinfo | grep Model
   free -h
   df -h
   vcgencmd measure_temp
   vcgencmd get_throttled
   ```

3. **Abra uma issue no GitHub:**
   - Inclua logs completos
   - Informações do sistema
   - Configurações usadas
   - Passos para reproduzir

---

**Dica:** A maioria dos problemas é causada por:
1. 🔥 Temperatura alta (80%+)
2. 🔌 Alimentação fraca (15%)
3. ⚙️ Configuração incorreta (5%)

Sempre comece verificando temperatura e alimentação!
