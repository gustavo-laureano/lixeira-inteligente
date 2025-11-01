"""
Servidor Broker de WebSockets para Controle de Robô
Atua como intermediário entre controladores (web) e robôs (Raspberry Pi)
"""

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from typing import Set
import logging

# Configuração de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="API Broker - Sistema de Controle de Robô")

# Adiciona CORS para permitir conexões de qualquer origem (incluindo file://)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Permite qualquer origem
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Gerenciamento de conexões WebSocket
class ConnectionManager:
    def __init__(self):
        # Lista de controladores (interfaces web)
        self.controllers: Set[WebSocket] = set()
        # Lista de robôs (Raspberry Pi)
        self.robots: Set[WebSocket] = set()
    
    async def connect_controller(self, websocket: WebSocket):
        """Adiciona um controlador à lista"""
        await websocket.accept()
        self.controllers.add(websocket)
        logger.info(f"Controlador conectado. Total: {len(self.controllers)}")
    
    async def connect_robot(self, websocket: WebSocket):
        """Adiciona um robô à lista"""
        await websocket.accept()
        self.robots.add(websocket)
        logger.info(f"Robô conectado. Total: {len(self.robots)}")
    
    def disconnect_controller(self, websocket: WebSocket):
        """Remove um controlador da lista"""
        self.controllers.discard(websocket)
        logger.info(f"Controlador desconectado. Total: {len(self.controllers)}")
    
    def disconnect_robot(self, websocket: WebSocket):
        """Remove um robô da lista"""
        self.robots.discard(websocket)
        logger.info(f"Robô desconectado. Total: {len(self.robots)}")
    
    async def broadcast_to_robots(self, message: str):
        """Transmite uma mensagem para TODOS os robôs conectados"""
        if not self.robots:
            logger.warning("Nenhum robô conectado para receber a mensagem")
            return
        
        # Envia para todos os robôs simultaneamente
        disconnected = set()
        for robot in self.robots:
            try:
                await robot.send_text(message)
            except Exception as e:
                logger.error(f"Erro ao enviar para robô: {e}")
                disconnected.add(robot)
        
        # Remove robôs desconectados
        for robot in disconnected:
            self.disconnect_robot(robot)
    
    async def send_to_controller(self, websocket: WebSocket, message: str):
        """Envia uma mensagem para um controlador específico"""
        try:
            await websocket.send_text(message)
        except Exception as e:
            logger.error(f"Erro ao enviar para controlador: {e}")
            self.disconnect_controller(websocket)

# Instância global do gerenciador
manager = ConnectionManager()

@app.websocket("/ws/controller")
async def websocket_controller(websocket: WebSocket):
    """
    Endpoint para conexão de controladores (interfaces web)
    """
    logger.info(f"Tentativa de conexão WebSocket em /ws/controller")
    await manager.connect_controller(websocket)
    
    try:
        while True:
            # Recebe mensagem do controlador
            data = await websocket.receive_text()
            
            # Teste de latência: ping/pong
            if data == "ping":
                await manager.send_to_controller(websocket, "pong")
                logger.debug("Respondeu ping com pong")
            else:
                # Comandos normais: transmite para todos os robôs
                await manager.broadcast_to_robots(data)
                logger.debug(f"Comando transmitido para robôs: {data}")
    
    except WebSocketDisconnect:
        manager.disconnect_controller(websocket)
        logger.info("Controlador desconectado")
    except Exception as e:
        logger.error(f"Erro no WebSocket controller: {e}")
        manager.disconnect_controller(websocket)

@app.websocket("/ws/robot")
async def websocket_robot(websocket: WebSocket):
    """
    Endpoint para conexão de robôs (Raspberry Pi)
    """
    logger.info(f"Tentativa de conexão WebSocket em /ws/robot")
    await manager.connect_robot(websocket)
    
    try:
        while True:
            # Escuta mensagens do robô (pode ser usado para telemetria)
            data = await websocket.receive_text()
            logger.debug(f"Recebido do robô: {data}")
            # Aqui você pode processar dados de telemetria se necessário
    
    except WebSocketDisconnect:
        manager.disconnect_robot(websocket)
        logger.info("Robô desconectado")
    except Exception as e:
        logger.error(f"Erro no WebSocket robot: {e}")
        manager.disconnect_robot(websocket)

@app.get("/")
async def root():
    """Endpoint raiz - informações do servidor"""
    return {
        "status": "online",
        "controllers_connected": len(manager.controllers),
        "robots_connected": len(manager.robots),
        "endpoints": {
            "controller": "/ws/controller",
            "robot": "/ws/robot"
        }
    }

@app.get("/health")
async def health():
    """Endpoint de health check"""
    return {
        "status": "healthy",
        "controllers": len(manager.controllers),
        "robots": len(manager.robots)
    }

if __name__ == "__main__":
    import uvicorn
    logger.info("Iniciando servidor...")
    logger.info("WebSocket endpoints disponíveis:")
    logger.info("  - ws://0.0.0.0:8000/ws/controller")
    logger.info("  - ws://0.0.0.0:8000/ws/robot")
    # Roda na porta 8000 por padrão
    # Para acessar de outros dispositivos, use 0.0.0.0
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")

