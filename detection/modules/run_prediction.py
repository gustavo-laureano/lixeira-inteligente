import cv2
import time
import matplotlib.pyplot as plt
from ultralytics import YOLO
from . import config
from .spatial import SpatialProcessor
from .physics import PhysicsPredictor
from . import model_loader


class Visualizer3D:
    """Classe reutilizável para visualização 3D de trajetórias"""
    
    def __init__(self, axis_limits=2.0, height_limit=3.0):
        """
        Args:
            axis_limits: Limite dos eixos X e Y (metros)
            height_limit: Limite do eixo Z (metros)
        """
        self.axis_limits = axis_limits
        self.height_limit = height_limit
        
        self.fig = None
        self.ax_3d = None
        self.initialized = False
    
    def initialize(self):
        """Inicializa a visualização 3D"""
        if not self.initialized:
            plt.ion()  # Modo interativo
            self.fig = plt.figure(figsize=(10, 8))
            self.ax_3d = self.fig.add_subplot(111, projection='3d')
            self.initialized = True
            print("🎨 Visualização 3D inicializada")
    
    def update(self, current_pos=None, trajectory=None, landing_pos=None):
        """
        Atualiza a visualização 3D
        
        Args:
            current_pos: Tuple (x, y, z) da posição atual do objeto
            trajectory: Lista de tuples [(x, y, z), ...] da trajetória prevista
            landing_pos: Tuple (x, y, z) do ponto de impacto
        """
        if not self.initialized:
            return
        
        try:
            self.ax_3d.clear()
            
            # Configurar limites e labels
            self.ax_3d.set_xlim(-self.axis_limits, self.axis_limits)
            self.ax_3d.set_ylim(-self.axis_limits, self.axis_limits)
            self.ax_3d.set_zlim(0, self.height_limit)
            self.ax_3d.set_xlabel('X (m)')
            self.ax_3d.set_ylabel('Y (m)')
            self.ax_3d.set_zlabel('Z (Altura)')
            self.ax_3d.set_title("Trajetória Prevista - Lixeira Inteligente")
            
            # Origem (Câmera/Robô)
            self.ax_3d.scatter([0], [0], [0], c='black', marker='^', s=100, label='Robô')
            
            # Objeto atual (Vermelho)
            if current_pos is not None:
                x, y, z = current_pos
                self.ax_3d.scatter([x], [y], [z], c='red', s=150, label='Objeto Atual')
            
            # Trajetória prevista (Linha Verde)
            if trajectory and len(trajectory) > 0:
                tx = [p[0] for p in trajectory]
                ty = [p[1] for p in trajectory]
                tz = [p[2] for p in trajectory]
                self.ax_3d.plot(tx, ty, tz, c='green', linewidth=2, label='Trajetória')
            
            # Ponto de impacto (X Verde)
            if landing_pos is not None:
                lx, ly, lz = landing_pos
                self.ax_3d.scatter([lx], [ly], [lz], c='green', marker='X', s=300, linewidth=4)
                self.ax_3d.text(lx, ly, lz, f"  ALVO\n  ({lx:.2f}, {ly:.2f})", 
                               color='green', fontsize=10)
            
            self.ax_3d.legend()
            plt.pause(0.001)  # Atualizar sem bloquear
            
        except Exception as e:
            print(f"⚠️  Erro ao atualizar visualização 3D: {e}")
    
    def close(self):
        """Fecha a visualização 3D"""
        if self.initialized:
            plt.close(self.fig)
            self.fig = None
            self.ax_3d = None
            self.initialized = False
            print("🎨 Visualização 3D fechada")
    
    def is_active(self):
        """Retorna se a visualização está ativa"""
        return self.initialized

def main():
    print("Inicializando Sistema de Interceptação...")
    
    # 1. Carregar Módulos
    model = model_loader.load_yolo_model(config.MODEL_PATH)
    spatial = SpatialProcessor()
    physics = TrajectoryPredictor()
    
    # 2. Câmera
    cap = cv2.VideoCapture(config.CAMERA_ID)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, config.CAMERA_WIDTH)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, config.CAMERA_HEIGHT)
    
    # Configurações de Luz (Mantenha as suas que funcionaram!)
    cap.set(cv2.CAP_PROP_AUTOFOCUS, 0)
    cap.set(cv2.CAP_PROP_AUTO_EXPOSURE, 0.25) 
    cap.set(cv2.CAP_PROP_EXPOSURE, -5.0) 

    # 3. Gráfico 3D
    plt.ion()
    fig = plt.figure(figsize=(12, 6))
    ax_3d = fig.add_subplot(1, 2, 2, projection='3d')
    ax_cam = fig.add_subplot(1, 2, 1)
    cam_plot = None

    try:
        while True:
            ret, frame = cap.read()
            if not ret: break
            current_time = time.time()

            # --- A. VISÃO ---
            results = model(frame, verbose=False, conf=config.CONFIDENCE_THRESHOLD)
            annotated_frame = results[0].plot()
            frame_rgb = cv2.cvtColor(annotated_frame, cv2.COLOR_BGR2RGB)

            coords = None
            landing_spot = None
            trajectory_line = []

            # --- B. ESPACIAL ---
            if len(results[0].boxes) > 0:
                det = results[0].boxes[0]
                box = det.xyxy[0].cpu().numpy()
                cls_id = int(det.cls[0])
                
                coords = spatial.pixel_to_world(box, cls_id)

            # --- C. FÍSICA ---
            if coords:
                x, y, z = coords
                # Adiciona ao histórico
                physics.add_point(x, y, z, current_time)
                
                # Calcula o futuro!
                landing_spot, trajectory_line = physics.predict()

            # --- D. INTEGRAÇÃO COM ROBÔ (Simulado) ---
            if landing_spot:
                lx, ly = landing_spot
                # AQUI É ONDE VOCÊ MANDA O COMANDO PRO CARRINHO
                # Ex: serial_port.write(f"GOTO {lx:.2f} {ly:.2f}\n")
                cv2.putText(annotated_frame, f"PREVISAO: X={lx:.2f} Y={ly:.2f}", (10, 30), 
                            cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                
                # Atualiza frame RGB com o texto novo
                frame_rgb = cv2.cvtColor(annotated_frame, cv2.COLOR_BGR2RGB)

            # --- E. VISUALIZAÇÃO 3D ---
            if cam_plot is None:
                cam_plot = ax_cam.imshow(frame_rgb)
                ax_cam.axis('off')
            else:
                cam_plot.set_data(frame_rgb)

            ax_3d.clear()
            ax_3d.set_xlim(-1.0, 1.0)
            ax_3d.set_ylim(-1.0, 1.0)
            ax_3d.set_zlim(0, 2.5)
            ax_3d.set_xlabel('X (m)')
            ax_3d.set_ylabel('Y (m)')
            ax_3d.set_zlabel('Z (Altura)')
            ax_3d.set_title("Trajetória Prevista")

            # Câmera/Robô (Origem)
            ax_3d.scatter([0], [0], [0], c='black', marker='^', s=50)

            # Objeto Real (Vermelho)
            if coords:
                ax_3d.scatter([coords[0]], [coords[1]], [coords[2]], c='red', s=100, label='Atual')

            # Trajetória Prevista (Linha Verde)
            if trajectory_line:
                tx = [p[0] for p in trajectory_line]
                ty = [p[1] for p in trajectory_line]
                tz = [p[2] for p in trajectory_line]
                ax_3d.plot(tx, ty, tz, c='green', linewidth=2, label='Previsão')

            # Ponto de Impacto (X Verde)
            if landing_spot:
                ax_3d.scatter([landing_spot[0]], [landing_spot[1]], [0], c='green', marker='x', s=200, linewidth=3)
                ax_3d.text(landing_spot[0], landing_spot[1], 0, "  ALVO", color='green')

            plt.pause(0.001)

    except KeyboardInterrupt:
        print("Finalizando...")
    finally:
        cap.release()
        plt.close()
        cv2.destroyAllWindows()

if __name__ == "__main__":
    main()