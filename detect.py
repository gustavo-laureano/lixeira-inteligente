#!/usr/bin/env python3
"""
Sistema de Detecção YOLO para Lixeira Inteligente
Otimizado para Raspberry Pi com câmera 480p
Comunica com Arduino via Serial
"""

import cv2
import yaml
import time
import serial
import logging
from pathlib import Path
from ultralytics import YOLO
import numpy as np

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/app/logs/detection.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class ObjectDetector:
    """Classe para detecção de objetos usando YOLO"""
    
    def __init__(self, config_path='config.yaml'):
        """Inicializa o detector"""
        self.config = self._load_config(config_path)
        self.model = None
        self.camera = None
        self.serial_conn = None
        self.fps_counter = []
        
    def _load_config(self, config_path):
        """Carrega configurações do arquivo YAML"""
        try:
            with open(config_path, 'r') as f:
                config = yaml.safe_load(f)
            logger.info(f"Configuração carregada de {config_path}")
            return config
        except Exception as e:
            logger.error(f"Erro ao carregar config: {e}")
            # Configuração padrão
            return {
                'camera': {
                    'resolution': [640, 480],
                    'fps': 30,
                    'device': 0
                },
                'yolo': {
                    'model': 'yolov8n.pt',
                    'confidence': 0.5,
                    'iou': 0.45
                },
                'serial': {
                    'port': '/dev/ttyUSB0',
                    'baudrate': 9600,
                    'timeout': 1
                },
                'detection': {
                    'classes': ['bottle', 'cup', 'can'],
                    'min_area': 1000
                }
            }
    
    def setup_camera(self):
        """Configura a câmera"""
        try:
            cam_config = self.config['camera']
            self.camera = cv2.VideoCapture(cam_config['device'])
            
            # Configura resolução 480p
            width, height = cam_config['resolution']
            self.camera.set(cv2.CAP_PROP_FRAME_WIDTH, width)
            self.camera.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
            self.camera.set(cv2.CAP_PROP_FPS, cam_config['fps'])
            
            # Otimizações para Raspberry Pi
            self.camera.set(cv2.CAP_PROP_BUFFERSIZE, 1)
            
            if not self.camera.isOpened():
                raise Exception("Não foi possível abrir a câmera")
            
            logger.info(f"Câmera configurada: {width}x{height} @ {cam_config['fps']}fps")
            return True
        except Exception as e:
            logger.error(f"Erro ao configurar câmera: {e}")
            return False
    
    def setup_model(self):
        """Carrega o modelo YOLO"""
        try:
            yolo_config = self.config['yolo']
            model_path = f"/app/models/{yolo_config['model']}"
            
            # Se o modelo não existe, baixa automaticamente
            if not Path(model_path).exists():
                logger.info(f"Baixando modelo {yolo_config['model']}...")
                self.model = YOLO(yolo_config['model'])
            else:
                self.model = YOLO(model_path)
            
            logger.info(f"Modelo YOLO carregado: {yolo_config['model']}")
            return True
        except Exception as e:
            logger.error(f"Erro ao carregar modelo: {e}")
            return False
    
    def setup_serial(self):
        """Configura comunicação serial com Arduino"""
        try:
            serial_config = self.config['serial']
            self.serial_conn = serial.Serial(
                port=serial_config['port'],
                baudrate=serial_config['baudrate'],
                timeout=serial_config['timeout']
            )
            time.sleep(2)  # Aguarda Arduino resetar
            logger.info(f"Comunicação serial estabelecida: {serial_config['port']}")
            return True
        except Exception as e:
            logger.warning(f"Erro ao configurar serial: {e}")
            logger.warning("Continuando sem comunicação serial")
            return False
    
    def send_command(self, command):
        """Envia comando para o Arduino"""
        if self.serial_conn and self.serial_conn.is_open:
            try:
                self.serial_conn.write(f"{command}\n".encode())
                logger.debug(f"Comando enviado: {command}")
                
                # Aguarda resposta
                if self.serial_conn.in_waiting:
                    response = self.serial_conn.readline().decode().strip()
                    logger.debug(f"Resposta Arduino: {response}")
                    return response
            except Exception as e:
                logger.error(f"Erro ao enviar comando: {e}")
        return None
    
    def process_detection(self, results):
        """Processa resultados da detecção e toma decisões"""
        yolo_config = self.config['yolo']
        detection_config = self.config['detection']
        target_classes = detection_config['classes']
        
        for result in results:
            boxes = result.boxes
            
            if boxes is None or len(boxes) == 0:
                continue
            
            for box in boxes:
                # Extrai informações da detecção
                conf = float(box.conf[0])
                cls = int(box.cls[0])
                class_name = result.names[cls]
                
                # Verifica se é uma classe de interesse
                if class_name not in target_classes:
                    continue
                
                # Verifica confiança mínima
                if conf < yolo_config['confidence']:
                    continue
                
                # Calcula área do objeto
                x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
                area = (x2 - x1) * (y2 - y1)
                
                # Verifica área mínima
                if area < detection_config['min_area']:
                    continue
                
                # Calcula posição central do objeto
                center_x = (x1 + x2) / 2
                frame_width = self.config['camera']['resolution'][0]
                
                # Determina direção (esquerda, centro, direita)
                position = self._get_position(center_x, frame_width)
                
                # Determina distância baseada na área
                distance = self._get_distance(area)
                
                logger.info(f"Detectado: {class_name} (conf: {conf:.2f}, área: {area:.0f}, pos: {position}, dist: {distance})")
                
                # Envia comando para Arduino
                command = self._generate_command(class_name, position, distance)
                self.send_command(command)
                
                return {
                    'class': class_name,
                    'confidence': conf,
                    'position': position,
                    'distance': distance,
                    'area': area,
                    'bbox': (x1, y1, x2, y2)
                }
        
        return None
    
    def _get_position(self, center_x, frame_width):
        """Determina posição do objeto no frame"""
        third = frame_width / 3
        if center_x < third:
            return "LEFT"
        elif center_x > 2 * third:
            return "RIGHT"
        else:
            return "CENTER"
    
    def _get_distance(self, area):
        """Determina distância do objeto baseado na área em pixels"""
        detection_config = self.config['detection']
        thresholds = detection_config.get('distance_thresholds', {})
        
        very_close = thresholds.get('very_close', 50000)
        close = thresholds.get('close', 20000)
        medium = thresholds.get('medium', 10000)
        
        if area >= very_close:
            return "VERY_CLOSE"  # Muito perto - precisa recuar
        elif area >= close:
            return "CLOSE"        # Perto - parar ou ajustar posição
        elif area >= medium:
            return "MEDIUM"       # Distância média - aproximar devagar
        else:
            return "FAR"          # Longe - avançar rápido
    
    def _generate_command(self, class_name, position, distance):
        """Gera comando para o Arduino baseado na detecção"""
        # Formato: OBJETO:POSICAO:DISTANCIA
        return f"{class_name.upper()}:{position}:{distance}"
    
    def calculate_fps(self):
        """Calcula FPS atual"""
        current_time = time.time()
        self.fps_counter.append(current_time)
        
        # Mantém apenas último segundo
        self.fps_counter = [t for t in self.fps_counter if current_time - t < 1.0]
        
        return len(self.fps_counter)
    
    def run(self):
        """Loop principal de detecção"""
        logger.info("Iniciando sistema de detecção...")
        
        # Inicializa componentes
        if not self.setup_camera():
            logger.error("Falha ao inicializar câmera")
            return
        
        if not self.setup_model():
            logger.error("Falha ao carregar modelo")
            return
        
        self.setup_serial()  # Serial é opcional
        
        logger.info("Sistema pronto! Iniciando detecção...")
        
        try:
            frame_count = 0
            yolo_config = self.config['yolo']
            
            while True:
                # Captura frame
                ret, frame = self.camera.read()
                if not ret:
                    logger.warning("Falha ao capturar frame")
                    continue
                
                frame_count += 1
                
                # Executa detecção
                results = self.model(
                    frame,
                    conf=yolo_config['confidence'],
                    iou=yolo_config['iou'],
                    verbose=False
                )
                
                # Processa resultados
                detection = self.process_detection(results)
                
                # Calcula e exibe FPS
                fps = self.calculate_fps()
                if frame_count % 30 == 0:
                    logger.info(f"FPS: {fps}")
                
                # Pequeno delay para não sobrecarregar
                time.sleep(0.001)
                
        except KeyboardInterrupt:
            logger.info("Interrompido pelo usuário")
        except Exception as e:
            logger.error(f"Erro no loop principal: {e}")
        finally:
            self.cleanup()
    
    def cleanup(self):
        """Libera recursos"""
        logger.info("Finalizando sistema...")
        
        if self.camera:
            self.camera.release()
        
        if self.serial_conn and self.serial_conn.is_open:
            self.serial_conn.close()
        
        cv2.destroyAllWindows()
        logger.info("Sistema finalizado")


if __name__ == "__main__":
    detector = ObjectDetector()
    detector.run()
