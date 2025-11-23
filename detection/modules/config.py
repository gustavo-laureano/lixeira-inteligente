"""
Configurações centralizadas do sistema - Clean Code
"""

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
MAX_SPEED = 255  # Velocidade máxima (0-255)
KP_TURN = 150.0  # Ganho proporcional para rotação
KP_FORWARD = 200.0  # Ganho proporcional para movimento

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
