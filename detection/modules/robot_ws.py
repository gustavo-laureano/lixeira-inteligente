"""
Cliente WebSocket para comunicação com o robô
"""

import json
import threading
from time import sleep

try:
    import websocket
except ImportError:
    print("⚠️  websocket-client não instalado. Instale com: pip install websocket-client")
    websocket = None


class RobotWebSocket:
    """Cliente WebSocket para enviar comandos ao robô"""
    
    def __init__(self, url, auto_reconnect=True):
        """
        Args:
            url: URL do WebSocket (ex: ws://localhost:8000/ws/controller)
            auto_reconnect: Reconectar automaticamente se perder conexão
        """
        self.url = url
        self.auto_reconnect = auto_reconnect
        
        self.ws = None
        self.connected = False
        self.reconnect_thread = None
        self.running = True
    
    def connect(self):
        """Estabelece conexão com o servidor"""
        if websocket is None:
            print("❌ WebSocket não disponível. Modo offline.")
            return False
        
        try:
            print(f"🔌 Conectando ao robô em {self.url}...")
            self.ws = websocket.WebSocket()
            self.ws.connect(self.url, timeout=5)
            self.connected = True
            print("✅ Conectado ao robô!")
            return True
            
        except Exception as e:
            print(f"❌ Erro ao conectar: {e}")
            self.connected = False
            
            if self.auto_reconnect:
                self._start_reconnect_thread()
            
            return False
    
    def _start_reconnect_thread(self):
        """Inicia thread de reconexão automática"""
        if self.reconnect_thread is None or not self.reconnect_thread.is_alive():
            self.reconnect_thread = threading.Thread(target=self._reconnect_loop, daemon=True)
            self.reconnect_thread.start()
    
    def _reconnect_loop(self):
        """Loop de reconexão automática"""
        while self.running and not self.connected:
            print("🔄 Tentando reconectar...")
            sleep(5)
            self.connect()
    
    def send_raw(self, text: str):
        """
        Envia texto puro ao robô (sem conversão JSON)
        
        Args:
            text: String no formato "V:vy,vx"
        """
        if not self.connected or self.ws is None:
            return False
        
        try:
            self.ws.send(text)
            return True
            
        except Exception as e:
            print(f"⚠️  Erro ao enviar comando: {e}")
            self.connected = False
            
            if self.auto_reconnect:
                self._start_reconnect_thread()
            
            return False
    
    def send_motor_speeds(self, left_speed, right_speed):
        """
        Envia velocidades diretas aos motores
        
        Args:
            left_speed: Velocidade motor esquerdo (-255 a 255)
            right_speed: Velocidade motor direito (-255 a 255)
        """
        command = {
            'left': int(left_speed),
            'right': int(right_speed)
        }
        return self.send_command(command)
    
    def stop(self):
        """Para o robô"""
        return self.send_motor_speeds(0, 0)
    
    def disconnect(self):
        """Desconecta do servidor"""
        self.running = False
        
        if self.ws:
            try:
                self.stop()  # Para o robô antes de desconectar
                self.ws.close()
                print("🔌 Desconectado do robô")
            except:
                pass
        
        self.connected = False
    
    def is_connected(self):
        """Retorna se está conectado"""
        return self.connected
    
    def __enter__(self):
        """Context manager"""
        self.connect()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager cleanup"""
        self.disconnect()
