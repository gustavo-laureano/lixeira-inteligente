# Dockerfile otimizado para Raspberry Pi com YOLO
# Usa imagem base leve com Python 3.9
FROM python:3.9-slim-bullseye

# Variáveis de ambiente para otimização
ENV PYTHONUNBUFFERED=1 \
    DEBIAN_FRONTEND=noninteractive \
    # OpenCV otimizações
    OPENCV_VIDEOIO_PRIORITY_MSMF=0 \
    # Desabilita GUI warnings
    QT_QPA_PLATFORM=offscreen

# Instala dependências do sistema necessárias
RUN apt-get update && apt-get install -y --no-install-recommends \
    # Bibliotecas para OpenCV
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libgomp1 \
    libgstreamer1.0-0 \
    libgstreamer-plugins-base1.0-0 \
    # Ferramentas para câmera
    v4l-utils \
    # Ferramentas para comunicação serial
    udev \
    && rm -rf /var/lib/apt/lists/*

# Cria diretório de trabalho
WORKDIR /app

# Copia requirements primeiro (aproveita cache do Docker)
COPY requirements.txt .

# Instala dependências Python
RUN pip install --no-cache-dir -r requirements.txt

# Copia o código da aplicação
COPY . .

# Cria diretórios necessários
RUN mkdir -p /app/models /app/logs /app/data

# Comando padrão
CMD ["python", "detect.py"]
