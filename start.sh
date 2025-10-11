#!/bin/bash

# Script de inicialização rápida para Raspberry Pi
# Executa verificações e inicia o sistema

echo "=========================================="
echo "  Lixeira Inteligente - Inicialização"
echo "=========================================="
echo ""

# Cores
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Função de verificação
check_command() {
    if command -v $1 &> /dev/null; then
        echo -e "${GREEN}✓${NC} $1 instalado"
        return 0
    else
        echo -e "${RED}✗${NC} $1 NÃO instalado"
        return 1
    fi
}

# Verificações
echo "Verificando dependências..."
check_command docker
check_command docker-compose
check_command git

echo ""
echo "Verificando dispositivos..."

# Câmera
if [ -e /dev/video0 ]; then
    echo -e "${GREEN}✓${NC} Câmera detectada: /dev/video0"
else
    echo -e "${YELLOW}⚠${NC} Câmera não detectada em /dev/video0"
fi

# Serial
if ls /dev/ttyUSB* &> /dev/null || ls /dev/ttyACM* &> /dev/null; then
    echo -e "${GREEN}✓${NC} Porta serial detectada:"
    ls -l /dev/ttyUSB* /dev/ttyACM* 2>/dev/null | awk '{print "  " $NF}'
else
    echo -e "${YELLOW}⚠${NC} Nenhuma porta serial detectada"
fi

echo ""
echo "Criando diretórios..."
mkdir -p logs models data
echo -e "${GREEN}✓${NC} Diretórios criados"

echo ""
echo "=========================================="
echo "Opções:"
echo "=========================================="
echo "1. Testar câmera"
echo "2. Testar comunicação serial"
echo "3. Build Docker image"
echo "4. Iniciar sistema (docker-compose up)"
echo "5. Ver logs"
echo "6. Parar sistema"
echo "7. Sair"
echo ""

read -p "Escolha uma opção [1-7]: " option

case $option in
    1)
        echo "Testando câmera..."
        if command -v python3 &> /dev/null; then
            python3 test_camera.py
        else
            echo -e "${RED}Python3 não instalado!${NC}"
        fi
        ;;
    2)
        echo "Testando serial..."
        read -p "Porta serial [/dev/ttyUSB0]: " port
        port=${port:-/dev/ttyUSB0}
        if command -v python3 &> /dev/null; then
            python3 test_serial.py $port
        else
            echo -e "${RED}Python3 não instalado!${NC}"
        fi
        ;;
    3)
        echo "Building Docker image..."
        docker-compose build
        ;;
    4)
        echo "Iniciando sistema..."
        docker-compose up -d
        echo ""
        echo -e "${GREEN}✓${NC} Sistema iniciado!"
        echo "Use 'docker-compose logs -f' para ver os logs"
        ;;
    5)
        echo "Mostrando logs (Ctrl+C para sair)..."
        docker-compose logs -f
        ;;
    6)
        echo "Parando sistema..."
        docker-compose down
        echo -e "${GREEN}✓${NC} Sistema parado"
        ;;
    7)
        echo "Saindo..."
        exit 0
        ;;
    *)
        echo -e "${RED}Opção inválida!${NC}"
        exit 1
        ;;
esac
