"""
Sistema de detecção e rastreamento 3D - Lixeira Inteligente
Arquitetura Otimizada: Visualização desacoplada do processamento
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
        
        # Contador para limitar a taxa de atualização do gráfico 3D
        self.viz_counter = 0
        self.VIZ_SKIP_FRAMES = 4  # Atualiza o gráfico 3D a cada 5 frames (salva muita CPU)
        
        # Componentes
        self.camera = None
        self.detector = None
        self.spatial = None
        self.physics = None
        self.robot = None
        
        self.visualizer = Visualizer3D(
            axis_limits=config.AXIS_LIMITS,
            height_limit=config.HEIGHT_LIMIT
        )
        
    def initialize(self):
        """Inicializa todos os componentes do sistema"""
        print("=== Inicializando Lixeira Inteligente ===")
        
        # 1. Câmera
        print(f"\n[1/4] Inicializando câmera {config.CAMERA_ID}...")
        self.camera = CameraManager(
            src=config.CAMERA_ID,
            size=config.CAMERA_WIDTH,
            fps=config.CAMERA_FPS
        )
        self.camera.start()
        
        # 2. YOLO
        print(f"\n[2/4] Carregando modelo {config.MODEL_PATH}...")
        self.detector = load_yolo_model(config.MODEL_PATH)
        
        # 3. Processadores
        print("\n[3/4] Inicializando processadores 3D...")
        self.spatial = SpatialProcessor(config.CAMERA_WIDTH, config.CAMERA_HEIGHT, config.FOCAL_LENGTH)
        self.physics = PhysicsPredictor(config.HISTORY_SIZE, config.ROBOT_HEIGHT, config.GRAVITY)
        
        # 4. Robô
        print(f"\n[4/4] Conectando ao robô em {config.API_URL}...")
        self.robot = RobotWebSocket(config.API_URL)
        self.robot.connect()
        
        print("\n✅ Sistema inicializado com sucesso!")
        self._print_controls()
        
        if self.dev_mode:
            self.visualizer.initialize()
        
        return True
    
    def _print_controls(self):
        print("\n=== CONTROLES ===")
        print("  ESC    - Sair")
        print("  ESPAÇO - Pausar/Continuar")
        print("  D      - Dev Mode (Ligar/Desligar 3D)")
        print("=" * 40)
    
    def process_frame(self, frame):
        """Processa um frame completo"""
        if frame is None:
            return None
        
        # Detectar objetos (YOLO)
        results = self.detector.track(
            frame, 
            persist=True, 
            tracker="bytetrack.yaml", 
            verbose=False, 
            device=config.DEVICE,
            imgsz=320,     
            conf=0.25,      
            iou=0.5,
            classes=[0, 1]
        )
        
        self.viz_counter += 1
        should_update_3d = (self.viz_counter % self.VIZ_SKIP_FRAMES == 0)

        for result in results:
            boxes = result.boxes
            
            for box in boxes:
                # Extrair dados
                class_id = int(box.cls)
                confidence = float(box.conf)
                
                # Bbox segura
                xyxy = box.xyxy
                if hasattr(xyxy, 'detach'): xyxy = xyxy.detach().cpu().numpy()
                xyxy = np.squeeze(np.asarray(xyxy))
                
                if xyxy.ndim != 1 or xyxy.size < 4: continue
                
                x1, y1, x2, y2 = map(int, xyxy[:4])
                bbox = (x1, y1, x2, y2)
                
                # 3D Calculation
                obj_size = config.OBJECT_DIMENSIONS.get(class_id, config.DEFAULT_OBJECT_SIZE)
                pos_3d = self.spatial.calculate_3d_position(bbox, obj_size)
                
                if pos_3d is not None:
                    x, y, z = pos_3d
                    pos_3d_array = np.array([x, y, z])
                    
                    # Física e Predição
                    self.physics.add_point(pos_3d_array)
                    landing = self.physics.predict_landing()
                    
                    # Envia comando ao robô (PRIORIDADE ALTA - Sempre executa)
                    if not self.paused and landing is not None:
                        self._send_robot_command(landing[:2])
                    
                    # Visualização 3D (PRIORIDADE BAIXA - Executa a cada N frames)
                    if self.dev_mode and self.visualizer.is_active() and should_update_3d:
                        trajectory = self.physics.predict_trajectory()
                        landing_3d = landing if landing is not None else None
                        
                        self.visualizer.update(
                            current_pos=(x, y, z),
                            trajectory=[(p[0], p[1], p[2]) for p in trajectory] if len(trajectory) > 0 else None,
                            landing_pos=landing_3d
                        )
                    
                    # Desenho 2D (Overlay no vídeo)
                    if self.dev_mode:
                        self._draw_detection(frame, bbox, class_id, confidence, pos_3d)
        
        self._draw_overlay(frame)
        return frame
    
    def _send_robot_command(self, landing_point):
        """Envia comando de movimento"""
        x_target, y_target = landing_point
        if self.robot and self.robot.connected:
            distance = np.sqrt(x_target**2 + y_target**2)
            if distance < 0.1:
                vx, vy = 0.0, 0.0
            else:
                max_distance = config.MAX_ROBOT_DISTANCE
                scale = min(distance / max_distance, 1.0)
                vx = (x_target / distance) * scale
                vy = (y_target / distance) * scale
            
            self.robot.send_raw(f"V:{vy:.3f},{vx:.3f}")
            if config.VERBOSE_LOGGING:
                print(f"🤖 Cmd: V:{vy:.3f},{vx:.3f}")
        
    def _draw_detection(self, frame, bbox, class_id, confidence, pos_3d):
        x1, y1, x2, y2 = map(int, bbox)
        cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
        
        label = f"{config.TARGET_CLASSES[class_id] if class_id < len(config.TARGET_CLASSES) else class_id} {confidence:.2f}"
        cv2.putText(frame, label, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
        
        cv2.putText(frame, f"3D: ({pos_3d[0]:.2f}, {pos_3d[1]:.2f}, {pos_3d[2]:.2f})", 
                   (x1, y2 + 20), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 255, 0), 1)
    
    def _draw_overlay(self, frame):
        h, w = frame.shape[:2]
        if config.SHOW_FPS:
            # Cor muda conforme FPS: Verde > 30, Amarelo > 15, Vermelho < 15
            color = (0, 255, 0) if self.current_fps > 30 else (0, 255, 255) if self.current_fps > 15 else (0, 0, 255)
            cv2.putText(frame, f"FPS: {self.current_fps:.1f}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, color, 2)
        
        if self.paused:
            cv2.putText(frame, "PAUSADO", (w//2 - 100, h//2), cv2.FONT_HERSHEY_DUPLEX, 2, (0, 0, 255), 3)
        
        if self.dev_mode:
            cv2.putText(frame, "DEV MODE (3D ON)", (w - 220, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 0, 255), 2)
    
    def handle_keyboard(self, key):
        if key == config.KEY_QUIT:
            self.running = False
        elif key == config.KEY_PAUSE:
            self.paused = not self.paused
        elif key == config.KEY_DEV_MODE or key == ord('D') or key == ord('d'):
            self.dev_mode = not self.dev_mode
            if self.dev_mode:
                self.visualizer.initialize()
            else:
                self.visualizer.close()
            print(f"🔧 Dev Mode: {'Ligado' if self.dev_mode else 'Desligado'}")
    
    def update_fps(self):
        self.fps_counter += 1
        elapsed = time() - self.fps_start_time
        if elapsed >= 1.0:
            self.current_fps = self.fps_counter / elapsed
            self.fps_counter = 0
            self.fps_start_time = time()
    
    def run(self):
        if not self.initialize(): return
        try:
            while self.running:
                frame = self.camera.get_frame() # Non-blocking agora!
                
                if frame is not None:
                    processed_frame = self.process_frame(frame)
                    if processed_frame is not None:
                        cv2.imshow("Lixeira Inteligente", processed_frame)
                    self.update_fps()
                
                key = cv2.waitKey(1) & 0xFF
                if key != 255: self.handle_keyboard(key)
                
        except KeyboardInterrupt:
            print("\n⚠️ Interrompido")
        finally:
            self.cleanup()
    
    def cleanup(self):
        print("\n🧹 Limpando...")
        try: cv2.destroyAllWindows()
        except: pass
        if self.camera: self.camera.stop()
        if self.robot: self.robot.disconnect()
        if self.visualizer: self.visualizer.close()
        print("✅ Fim.")

if __name__ == "__main__":
    DetectionApp().run()