"""
Cliente Receptor para Raspberry Pi
Escuta comandos do servidor broker e transmite para o Arduino via Serial
"""

import asyncio
import websockets
import serial
import serial.tools.list_ports
import logging
import sys
from typing import Optional

# ===== CONFIGURAÇÃO =====
# Ajuste estes valores conforme seu ambiente
SERVER_URI = "ws://192.168.1.100:8000/ws/robot"  # IP do PC/Servidor com a API
SERIAL_PORT = "/dev/ttyUSB0"  # Porta serial do Arduino
BAUDRATE = 115200  # Baudrate configurado no Arduino

# Configuração de reconexão
RECONNECT_DELAY = 5  # Segundos entre tentativas de reconexão
RECONNECT_MAX_ATTEMPTS = None  # None = tentar infinitamente

# ===== CONFIGURAÇÃO DE LOGGING =====
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

class RobotReceiver:
    def __init__(self, server_uri: str, serial_port: str, baudrate: int):
        self.server_uri = server_uri
        self.serial_port = serial_port
        self.baudrate = baudrate
        self.serial_conn: Optional[serial.Serial] = None
        self.websocket = None
        self.running = False
    
    def init_serial(self) -> bool:
        """Inicializa a conexão serial com o Arduino"""
        try:
            # Lista portas disponíveis se a porta especificada não existir
            if self.serial_port not in [port.device for port in serial.tools.list_ports.comports()]:
                logger.warning(f"Porta {self.serial_port} não encontrada. Portas disponíveis:")
                for port in serial.tools.list_ports.comports():
                    logger.warning(f"  - {port.device}")
                return False
            
            self.serial_conn = serial.Serial(
                port=self.serial_port,
                baudrate=self.baudrate,
                timeout=1,
                write_timeout=1
            )
            
            # Aguarda Arduino inicializar
            import time
            time.sleep(2)
            
            logger.info(f"✓ Serial conectado: {self.serial_port} @ {self.baudrate} baud")
            return True
        
        except serial.SerialException as e:
            logger.error(f"Erro ao conectar serial: {e}")
            return False
        except Exception as e:
            logger.error(f"Erro inesperado na serial: {e}")
            return False
    
    def close_serial(self):
        """Fecha a conexão serial"""
        if self.serial_conn and self.serial_conn.is_open:
            self.serial_conn.close()
            logger.info("Serial desconectado")
    
    def send_to_arduino(self, command: str):
        """Envia comando para o Arduino via serial"""
        if not self.serial_conn or not self.serial_conn.is_open:
            logger.warning("Serial não está conectado. Comando ignorado.")
            return
        
        try:
            # Formata o comando com \n conforme protocolo
            formatted_command = f"{command}\n"
            self.serial_conn.write(formatted_command.encode())
            logger.debug(f"Enviado para Arduino: {command}")
        
        except serial.SerialTimeoutException:
            logger.error("Timeout ao escrever na serial")
        except Exception as e:
            logger.error(f"Erro ao enviar comando serial: {e}")
    
    async def handle_message(self, message: str):
        """Processa mensagem recebida do WebSocket"""
        # Remove espaços em branco
        command = message.strip()
        
        # Valida apenas o novo protocolo de vetor V:vy,vx
        if command.lower().startswith('v:'):
            # Encaminha diretamente o vetor para o Arduino (ex.: V:1.0,0.0)
            # Validação simples: deve conter exatamente uma vírgula (vy,vx)
            if command.count(',') >= 1:
                self.send_to_arduino(command)
            else:
                logger.warning(f"Protocolo V: inválido (esperado V:vy,vx): {command}")
        else:
            logger.warning(f"Comando inválido ignorado: {command}")
    
    async def connect_websocket(self):
        """Conecta ao servidor WebSocket"""
        try:
            logger.info(f"Conectando ao servidor: {self.server_uri}")
            self.websocket = await websockets.connect(
                self.server_uri,
                ping_interval=20,
                ping_timeout=10
            )
            logger.info("✓ WebSocket conectado ao servidor")
            return True
        
        except websockets.exceptions.InvalidURI:
            logger.error(f"URI inválida: {self.server_uri}")
            return False
        except websockets.exceptions.ConnectionClosed:
            logger.warning("Conexão WebSocket fechada pelo servidor")
            return False
        except Exception as e:
            logger.error(f"Erro ao conectar WebSocket: {e}")
            return False
    
    async def run(self):
        """Loop principal do receptor"""
        self.running = True
        
        # Inicializa serial
        if not self.init_serial():
            logger.error("Falha ao inicializar serial. Encerrando.")
            return
        
        # Tenta conectar WebSocket com reconexão automática
        attempt = 0
        while self.running:
            if await self.connect_websocket():
                # Conexão bem-sucedida, escuta mensagens
                try:
                    async for message in self.websocket:
                        await self.handle_message(message)
                
                except websockets.exceptions.ConnectionClosed:
                    logger.warning("Conexão WebSocket fechada")
                except Exception as e:
                    logger.error(f"Erro no loop WebSocket: {e}")
            
            # Se chegou aqui, a conexão caiu ou falhou
            if not self.running:
                break
            
            # Reconexão automática
            attempt += 1
            if RECONNECT_MAX_ATTEMPTS and attempt >= RECONNECT_MAX_ATTEMPTS:
                logger.error("Número máximo de tentativas atingido")
                break
            
            logger.info(f"Tentando reconectar em {RECONNECT_DELAY} segundos... (tentativa {attempt})")
            await asyncio.sleep(RECONNECT_DELAY)
        
        # Limpeza
        self.close_serial()
        if self.websocket:
            await self.websocket.close()
    
    def stop(self):
        """Para o receptor"""
        self.running = False

async def main():
    """Função principal"""
    logger.info("=" * 50)
    logger.info("Receptor de Comandos - Raspberry Pi")
    logger.info("=" * 50)
    logger.info(f"Servidor: {SERVER_URI}")
    logger.info(f"Serial: {SERIAL_PORT} @ {BAUDRATE} baud")
    logger.info("=" * 50)
    
    receiver = RobotReceiver(SERVER_URI, SERIAL_PORT, BAUDRATE)
    
    try:
        await receiver.run()
    except KeyboardInterrupt:
        logger.info("\nInterrompido pelo usuário")
        receiver.stop()
    except Exception as e:
        logger.error(f"Erro fatal: {e}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())

