"""
Sistema de detecção e rastreamento 3D - Lixeira Inteligente
Arquitetura limpa com controles de teclado
"""

import cv2
import numpy as np
import sys
from time import time

# Imports locais
from modules.camera_manager import CameraManager
from modules.model_loader import load_yolo_model
from modules.spatial import SpatialProcessor
from modules.physics import PhysicsPredictor
from modules.robot_ws import RobotWebSocket
from modules.run_prediction import Visualizer3D
import modules.config as config


class DetectionApp:
    """Aplicação principal com gerenciamento de estados"""
    
    def __init__(self):
        self.paused = False
        self.dev_mode = config.DEFAULT_DEV_MODE
        self.running = True
        
        # FPS tracking
        self.fps_counter = 0
        self.fps_start_time = time()
        self.current_fps = 0.0
        
        # Componentes
        self.camera = None
        self.detector = None
        self.spatial = None
        self.physics = None
        self.robot = None
        
        # Visualização 3D (reutilizando classe existente!)
        self.visualizer = Visualizer3D(
            axis_limits=config.AXIS_LIMITS,
            height_limit=config.HEIGHT_LIMIT
        )
        
    def initialize(self):
        """Inicializa todos os componentes do sistema"""
        print("=== Inicializando Lixeira Inteligente ===")
        
        # 1. Usar câmera do config (sem GUI selector por enquanto)
        print(f"\n[1/4] Inicializando câmera {config.CAMERA_ID}...")
        self.camera = CameraManager(
            src=config.CAMERA_ID,
            size=config.CAMERA_WIDTH,
            fps=config.CAMERA_FPS
        )
        self.camera.start()
        
        # 2. Carregar detector YOLO
        print(f"\n[2/4] Carregando modelo {config.MODEL_PATH}...")
        self.detector = load_yolo_model(config.MODEL_PATH)
        
        # 3. Processadores 3D e física
        print("\n[3/4] Inicializando processadores 3D...")
        self.spatial = SpatialProcessor(
            config.CAMERA_WIDTH,
            config.CAMERA_HEIGHT,
            config.FOCAL_LENGTH
        )
        self.physics = PhysicsPredictor(
            config.HISTORY_SIZE,
            config.ROBOT_HEIGHT,
            config.GRAVITY
        )
        
        # 4. Conectar ao robô
        print(f"\n[4/4] Conectando ao robô em {config.API_URL}...")
        self.robot = RobotWebSocket(config.API_URL)
        self.robot.connect()
        
        print("\n✅ Sistema inicializado com sucesso!")
        self._print_controls()
        
        # Inicializar visualização 3D se dev mode estiver ativo
        if self.dev_mode:
            self.visualizer.initialize()
        
        return True
    
    def _print_controls(self):
        """Mostra os controles disponíveis"""
        print("\n=== CONTROLES ===")
        print("  ESC   - Sair")
        print("  ESPAÇO - Pausar/Continuar")
        print("  D     - Dev Mode (visualização 3D)")
        print("=" * 40)
    
    def process_frame(self, frame):
        """Processa um frame completo"""
        if frame is None:
            return None
        
        # Detectar objetos usando YOLO
        results = self.detector.track(
            frame, 
            persist=True, 
            tracker="bytetrack.yaml", 
            verbose=False, 
            device=config.DEVICE
        )        
        # Processar cada detecção
        for result in results:
            boxes = result.boxes
            
            for box in boxes:
                # Extrair informações da detecção
                track_id = box.id if box.id is not None else None
                class_id = int(box.cls)
                confidence = float(box.conf)
                
                # Converter bbox para numpy
                import torch
                if isinstance(box.xyxy, torch.Tensor):
                    xyxy = box.xyxy.detach().cpu().numpy()
                else:
                    xyxy = box.xyxy
                xyxy = np.squeeze(np.asarray(xyxy))
                
                if xyxy.ndim != 1 or xyxy.size < 4:
                    continue
                
                x1, y1, x2, y2 = map(int, xyxy[:4])
                bbox = (x1, y1, x2, y2)
                
                # Calcular posição 3D
                obj_size = config.OBJECT_DIMENSIONS.get(class_id, config.DEFAULT_OBJECT_SIZE)
                pos_3d = self.spatial.calculate_3d_position(bbox, obj_size)
                
                if pos_3d is not None:
                    x, y, z = pos_3d
                    pos_3d_array = np.array([x, y, z])
                    
                    # Adicionar ao histórico e prever trajetória
                    self.physics.add_point(pos_3d_array)
                    landing = self.physics.predict_landing()
                    trajectory = self.physics.predict_trajectory()
                    
                    # Atualizar visualização 3D (se dev mode ativo)
                    if self.dev_mode and self.visualizer.is_active():
                        landing_3d = landing if landing is not None else None
                        self.visualizer.update(
                            current_pos=(x, y, z),
                            trajectory=[(p[0], p[1], p[2]) for p in trajectory] if len(trajectory) > 0 else None,
                            landing_pos=landing_3d
                        )
                    
                    # Enviar comando ao robô (se não pausado)
                    if not self.paused and landing is not None:
                        self._send_robot_command(landing[:2])  # Passar apenas (x, y)
                    
                    # Desenhar visualizações (se dev mode)
                    if self.dev_mode:
                        self._draw_detection(frame, bbox, class_id, confidence, pos_3d)
        
        # Desenhar overlay
        self._draw_overlay(frame)
        
        return frame
    
    def _send_robot_command(self, landing_point):
        """Envia comando de movimento ao robô no formato correto V:vy,vx"""
        x_target, y_target = landing_point
        
        if self.robot and self.robot.connected:
            # Normalizar coordenadas para o espaço do robô
            # Assumindo que o robô está em (0,0) e olha para frente (+Y)
            
            # Calcular vetor de velocidade normalizado
            distance = np.sqrt(x_target**2 + y_target**2)
            
            if distance < 0.1:  # Muito perto, parar
                vx = 0.0
                vy = 0.0
            else:
                # Normalizar e escalar para velocidade máxima (0-1)
                max_distance = config.MAX_ROBOT_DISTANCE  # metros (ajuste conforme seu campo)
                scale = min(distance / max_distance, 1.0)
                
                # vx: movimento lateral (esquerda/direita)
                # vy: movimento frontal (frente/trás)
                vx = (x_target / distance) * scale
                vy = (y_target / distance) * scale
            
            # "V:vy,vx"
            command = f"V:{vy:.3f},{vx:.3f}"
            
            self.robot.send_raw(command)
            
            if config.VERBOSE_LOGGING:
                print(f"🤖 Comando enviado: {command} (alvo: x={x_target:.2f}, y={y_target:.2f})")
        
    def _draw_detection(self, frame, bbox, class_id, confidence, pos_3d):
        """Desenha visualização da detecção"""
        x1, y1, x2, y2 = map(int, bbox)
        
        # Bounding box
        cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
        
        # Label com nome da classe
        class_name = config.TARGET_CLASSES[class_id] if class_id < len(config.TARGET_CLASSES) else f"Class {class_id}"
        label = f"{class_name} {confidence:.2f}"
        cv2.putText(frame, label, (x1, y1 - 10),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
        
        # Posição 3D
        x, y, z = pos_3d
        pos_text = f"3D: ({x:.2f}, {y:.2f}, {z:.2f})"
        cv2.putText(frame, pos_text, (x1, y2 + 20),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 255, 0), 1)
    
    def _draw_overlay(self, frame):
        """Desenha overlay com informações do sistema"""
        h, w = frame.shape[:2]
        
        # FPS
        if config.SHOW_FPS:
            cv2.putText(frame, f"FPS: {self.current_fps:.1f}", (10, 30),
                       cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255), 2)
        
        # Status de pausa
        if self.paused:
            overlay = frame.copy()
            cv2.rectangle(overlay, (0, 0), (w, h), (0, 0, 0), -1)
            cv2.addWeighted(overlay, 0.5, frame, 0.5, 0, frame)
            
            text = "PAUSADO"
            text_size = cv2.getTextSize(text, cv2.FONT_HERSHEY_DUPLEX, 2, 3)[0]
            text_x = (w - text_size[0]) // 2
            text_y = (h + text_size[1]) // 2
            cv2.putText(frame, text, (text_x, text_y),
                       cv2.FONT_HERSHEY_DUPLEX, 2, (0, 0, 255), 3)
        
        # Dev mode indicator
        if self.dev_mode:
            cv2.putText(frame, "DEV MODE", (w - 180, 30),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 0, 255), 2)
    
    def handle_keyboard(self, key):
        """Gerencia eventos de teclado"""
        if key == config.KEY_QUIT:
            self.running = False
            print("\n🛑 Encerrando aplicação...")
        
        elif key == config.KEY_PAUSE:
            self.paused = not self.paused
            status = "PAUSADO" if self.paused else "ATIVO"
            print(f"\n⏸️  Sistema {status}")
        
        elif key == config.KEY_DEV_MODE or key == ord('D'):  # Aceita 'd' ou 'D'
            self.dev_mode = not self.dev_mode
            status = "ATIVADO" if self.dev_mode else "DESATIVADO"
            print(f"\n🔧 Dev Mode {status}")
            
            # Abrir ou fechar visualização 3D (usando classe reutilizável)
            if self.dev_mode:
                self.visualizer.initialize()
            else:
                self.visualizer.close()
    
    def update_fps(self):
        """Atualiza contador de FPS"""
        self.fps_counter += 1
        elapsed = time() - self.fps_start_time
        
        if elapsed >= 1.0:
            self.current_fps = self.fps_counter / elapsed
            self.fps_counter = 0
            self.fps_start_time = time()
    
    def run(self):
        """Loop principal da aplicação"""
        if not self.initialize():
            return
        
        try:
            # Criar janela antecipadamente para garantir foco
            cv2.namedWindow("Lixeira Inteligente", cv2.WINDOW_NORMAL)
            
            while self.running:
                # Capturar frame
                frame = self.camera.get_frame()
                
                if frame is not None:
                    # Processar frame
                    processed_frame = self.process_frame(frame)
                    
                    # Mostrar resultado
                    if processed_frame is not None:
                        cv2.imshow("Lixeira Inteligente", processed_frame)
                    
                    # Atualizar FPS
                    self.update_fps()
                
                # Verificar teclas (sempre, mesmo sem frame)
                key = cv2.waitKey(1) & 0xFF
                
                # Processar apenas teclas válidas (ignorar 255 que é "nenhuma tecla")
                if key < 255:
                    self.handle_keyboard(key)
        
        except KeyboardInterrupt:
            print("\n⚠️  Interrompido pelo usuário")
        
        finally:
            self.cleanup()
    
    def cleanup(self):
        """Limpa recursos"""
        print("\n🧹 Limpando recursos...")
        
        # CRÍTICO: Fechar janelas OpenCV PRIMEIRO (antes de parar threads)
        try:
            cv2.destroyAllWindows()
            cv2.waitKey(1)  # Processa eventos pendentes
        except Exception as e:
            print(f"⚠️  Erro ao fechar janelas OpenCV: {e}")
        
        # Depois parar câmera (thread-safe agora)
        try:
            if self.camera:
                self.camera.stop()
        except Exception as e:
            print(f"⚠️  Erro ao parar câmera: {e}")
        
        try:
            if self.robot:
                self.robot.disconnect()
        except Exception as e:
            print(f"⚠️  Erro ao desconectar robô: {e}")
        
        try:
            # Fechar visualização 3D (usando classe reutilizável)
            self.visualizer.close()
        except Exception as e:
            print(f"⚠️  Erro ao fechar visualização: {e}")
        
        print("✅ Encerrado com sucesso!")


def main():
    """Entry point"""
    app = DetectionApp()
    app.run()


if __name__ == "__main__":
    main()
