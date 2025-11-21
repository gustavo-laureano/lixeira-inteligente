import cv2 
import threading
import time
import numpy as np

DEFAULT_FPS = 30
DEFAULT_SIZE = 640


class CameraManager:
    """Gerenciador de câmera que captura frames em thread separada"""
    
    def __init__(self, src=0, size=DEFAULT_SIZE, fps=DEFAULT_FPS):
        self.src = src
        self.size = size
        self.fps = fps
        self.frame = None
        self.ret = False
        self.is_running = False
        self.lock = threading.Lock()
        
        # Inicializa câmera
        print(f"Inicializando câmera {src}...")
        self.cap = cv2.VideoCapture(self.src, cv2.CAP_DSHOW)
        
        if not self.cap.isOpened():
            raise ValueError(f"Erro: Não foi possível abrir a câmera {self.src}")
        
        # Aquece a câmera
        print("Aquecendo câmera...")
        for _ in range(10):
            self.cap.read()
        print("Câmera pronta!")
    
    def start(self):
        """Inicia a captura de frames em thread separada"""
        if self.is_running:
            print("Câmera já está rodando")
            return self
        
        self.is_running = True
        self.thread = threading.Thread(target=self._capture_loop, daemon=True)
        self.thread.start()
        print("Captura iniciada em thread separada")
        return self
    
    def _capture_loop(self):
        """Loop de captura (roda em thread separada)"""
        while self.is_running:
            ret, frame = self.cap.read()
            
            if ret:
                # Crop para quadrado (pega o centro da imagem)
                h, w = frame.shape[:2]
                size = min(h, w)
                start_x = (w - size) // 2
                start_y = (h - size) // 2
                frame = frame[start_y:start_y + size, start_x:start_x + size]
                
                # Redimensiona para o tamanho desejado
                frame = cv2.resize(frame, (self.size, self.size))
                
                # Atualiza frame com thread-safe
                with self.lock:
                    self.frame = frame
                    self.ret = ret
            
            # Controla FPS
            time.sleep(1 / self.fps)
    
    def read(self):
        """Retorna (ret, frame) - similar ao cv2.VideoCapture.read()"""
        with self.lock:
            if self.frame is None:
                return False, None
            return self.ret, self.frame.copy()
    
    def get_frame(self):
        """Retorna apenas o frame (None se não disponível)"""
        ret, frame = self.read()
        return frame if ret else None
    
    def stop(self):
        """Para a captura e libera recursos"""
        print("Parando câmera...")
        self.is_running = False
        
        if hasattr(self, 'thread'):
            self.thread.join(timeout=2.0)
        
        self.cap.release()
        print("Câmera liberada")
    
    def __enter__(self):
        return self.start()
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.stop()
    
    def __del__(self):
        if hasattr(self, 'cap'):
            self.stop()


if __name__ == "__main__":
    camera = CameraManager(src=0, size=DEFAULT_SIZE, fps=DEFAULT_FPS)
    camera.start()
    
    print("Capturando frames. Pressione 'q' para sair.")
    
    try:
        while True:
            frame = camera.get_frame()
            
            if frame is not None:
                cv2.putText(frame, "Camera Manager Test", (10, 30), 
                           cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
                cv2.imshow("Camera Manager", frame)
                
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break
            else:
                print("Aguardando frame...")
                time.sleep(0.1)
    finally:
        camera.stop()
        cv2.destroyAllWindows()