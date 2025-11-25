"""
Configurações centralizadas do sistema - Clean Code
"""
import torch
try:
    import torch_directml
    DEVICE = torch_directml.device()
    print(f"Configuração: Usando GPU AMD via DirectML ({DEVICE})")
except ImportError:
    DEVICE = 'cuda' if torch.cuda.is_available() else 'cpu'
    print(f"DirectML não encontrado. Usando: {DEVICE}")
    
# ===== CÂMERA =====
CAMERA_ID = 0
CAMERA_WIDTH = 640
CAMERA_HEIGHT = 640
CAMERA_FPS = 60

# ===== YOLO =====
MODEL_PATH = "./detection/models/below-trash-v2.pt"
CONFIDENCE_THRESHOLD = 0.30
TARGET_CLASSES = ['can', 'paper']

# ===== FÍSICA E 3D =====
FOCAL_LENGTH = 1000  # Distância focal calibrada (pixels)
GRAVITY = 9.81  # Aceleração da gravidade (m/s²)

# Dimensões reais dos objetos (metros)
OBJECT_DIMENSIONS = {
    0: 0.17,  # can (lata) - 17cm
    1: 0.10,  # paper (papel) - 10cm
}
DEFAULT_OBJECT_SIZE = 0.10

# Limites do espaço 3D (metros)
AXIS_LIMITS = 2.0
HEIGHT_LIMIT = 3.0

# ===== TRACKING E PREDIÇÃO =====
HISTORY_SIZE = 10  # Frames para calcular velocidade
ROBOT_HEIGHT = 0.0  # Altura onde o robô pega (metros)
PREDICTION_STEP = 0.05  # Resolução da trajetória (segundos)

# ===== CONTROLE DO ROBÔ =====
MAX_ROBOT_DISTANCE = 2.0  # Distância máxima do campo (metros)
MIN_DISTANCE_THRESHOLD = 0.1  # Distância mínima para considerar movimento (metros)


# ===== INTERFACE =====
# Controles de teclado
KEY_QUIT = 27  # ESC - Sair
KEY_PAUSE = ord(' ')  # ESPAÇO - Pausar/Despausar
KEY_DEV_MODE = ord('d')  # D - Toggle Dev Mode

# Configurações padrão da interface
DEFAULT_DEV_MODE = True  # Inicia com visualização 3D
SHOW_FPS = True
SHOW_BOXES = True
SHOW_TRAJECTORY = True

# ===== API/WEBSOCKET =====
API_URL = "ws://localhost:8000/ws/controller"
