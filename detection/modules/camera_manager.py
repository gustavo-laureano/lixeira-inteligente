import cv2
import threading
import time
import numpy as np
from queue import Queue, Empty

DEFAULT_FPS = 60
DEFAULT_SIZE = 416

class CameraManager:

    
    def __init__(self, src=0, size=DEFAULT_SIZE, fps=DEFAULT_FPS):
        self.src = src
        self.size = size
        self.fps = fps
        
        self.frame_queue = Queue(maxsize=1)
        
        self.is_running = False
        self.cap = None
        self.thread = None
        
        self._open_camera()
    
    def _open_camera(self):
        print(f"⚡ OTIMIZAÇÃO: Iniciando câmera {self.src}...")
        
        self.cap = cv2.VideoCapture(self.src)
        
        if not self.cap.isOpened():
            raise ValueError(f"❌ Erro fatal: Câmera {self.src} não abriu.")


        fourcc = cv2.VideoWriter_fourcc(*'MJPG')
        self.cap.set(cv2.CAP_PROP_FOURCC, fourcc)
        
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        
        # 3. FPS Solicitado
        self.cap.set(cv2.CAP_PROP_FPS, self.fps)
        
        # 4. Remove Buffer interno do OpenCV (para reduzir lag)
        self.cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)

        # Diagnóstico rápido
        actual_w = self.cap.get(cv2.CAP_PROP_FRAME_WIDTH)
        actual_h = self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
        actual_fps = self.cap.get(cv2.CAP_PROP_FPS)
        print(f"✅ Hardware configurado: {int(actual_w)}x{int(actual_h)} @ {actual_fps:.0f} FPS (Tentando MJPG)")

    def start(self):
        if self.is_running:
            return self
            
        self.is_running = True
        # Daemon=True garante que a thread morre se o programa principal morrer
        self.thread = threading.Thread(target=self._capture_loop, daemon=True)
        self.thread.start()
        return self
    
    def _capture_loop(self):
        """Loop ultra-rápido: Ler -> Resize Simples -> Queue"""
        
        # Pré-calcula variáveis para não gastar CPU dentro do loop
        target_size = (self.size, self.size)
        
        while self.is_running:
            ret, frame = self.cap.read()
            
            if not ret:
                # Se a câmera desconectar, tenta reconectar brevemente ou espera
                time.sleep(0.1)
                continue

            # OTIMIZAÇÃO DE RESIZE:
            # Se a imagem já vier quadrada ou perto disso, só faz o resize.
            # Se precisar cortar, fazemos o slice numpy (que é instantâneo).
            h, w = frame.shape[:2]
            
            # 1. Crop Quadrado Rápido (Centralizado)
            if w != h:
                min_side = min(h, w)
                off_x = (w - min_side) // 2
                off_y = (h - min_side) // 2
                frame = frame[off_y:off_y+min_side, off_x:off_x+min_side]

            # 2. Resize para 416
            # INTER_LINEAR é rápido. Se ainda estiver lento, mude para INTER_NEAREST (mas perde qualidade)
            frame = cv2.resize(frame, target_size, interpolation=cv2.INTER_LINEAR)
            
            # 3. Atualiza Queue (sem bloquear)
            # Se tiver cheio, limpa e põe o novo (garante frame mais recente)
            if not self.frame_queue.empty():
                try:
                    self.frame_queue.get_nowait()
                except Empty:
                    pass
            
            self.frame_queue.put(frame)

    def get_frame(self):
        """
        Retorna o último frame.
        Se não tiver frame pronto, retorna None (não bloqueia o programa principal).
        """
        try:
            return self.frame_queue.get_nowait()
        except Empty:
            return None
    
    def stop(self):
        self.is_running = False
        if self.thread and self.thread.is_alive():
            self.thread.join(timeout=1.0)
        
        if self.cap:
            self.cap.release()
        print("⏹️ Câmera parada.")


    @staticmethod
    def list_cameras(max_test=10):
        return [{'id': i} for i in range(max_test)] 