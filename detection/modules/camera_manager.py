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
        self.cap = None
        
        # Tenta abrir a câmera com diferentes backends
        self._open_camera()
    
    def _open_camera(self):
        """Tenta abrir a câmera com diferentes backends"""
        print(f"🔍 Tentando abrir câmera {self.src}...")
        
        # Lista de backends para tentar (ordem de prioridade)
        backends = [
            (cv2.CAP_DSHOW, "DirectShow (Windows)"),
            (cv2.CAP_MSMF, "Media Foundation (Windows)"),
            (cv2.CAP_ANY, "Auto-detect"),
        ]
        
        for backend, name in backends:
            print(f"  Tentando {name}...")
            try:
                self.cap = cv2.VideoCapture(self.src, backend)
                
                if self.cap.isOpened():
                    # Testa se consegue ler um frame
                    ret, test_frame = self.cap.read()
                    if ret and test_frame is not None:
                        print(f"  ✅ Câmera aberta com sucesso usando {name}")
                        
                        # Aquece a câmera
                        print("  Aquecendo câmera...")
                        for _ in range(10):
                            self.cap.read()
                        print("  ✅ Câmera pronta!")
                        return
                    else:
                        print(f"  ❌ Câmera abriu mas não consegue ler frames")
                        self.cap.release()
                else:
                    print(f"  ❌ Não conseguiu abrir com {name}")
            except Exception as e:
                print(f"  ❌ Erro ao tentar {name}: {e}")
        
        # Se chegou aqui, nenhum backend funcionou
        self._show_available_cameras()
        raise ValueError(
            f"❌ Erro: Não foi possível abrir a câmera {self.src}\n"
            f"Possíveis causas:\n"
            f"  1. Câmera não está conectada\n"
            f"  2. Câmera está sendo usada por outro programa\n"
            f"  3. ID da câmera incorreto (tente outro número)\n"
            f"  4. Drivers da câmera não instalados\n"
            f"\nTente fechar outros programas que podem estar usando a câmera."
        )
    
    @staticmethod
    def _show_available_cameras(max_test=5):
        """Lista câmeras disponíveis no sistema"""
        print("\n🔍 Procurando câmeras disponíveis...")
        available = []
        
        for i in range(max_test):
            try:
                cap = cv2.VideoCapture(i, cv2.CAP_ANY)
                if cap.isOpened():
                    ret, _ = cap.read()
                    if ret:
                        available.append(i)
                        print(f"  ✅ Câmera encontrada no ID: {i}")
                cap.release()
            except:
                pass
        
        if available:
            print(f"\n💡 Câmeras disponíveis: {available}")
            print(f"💡 Tente usar: CameraManager(src={available[0]})")
        else:
            print("\n❌ Nenhuma câmera encontrada no sistema")
            print("💡 Verifique se a câmera está conectada e os drivers instalados")
    
    @staticmethod
    def list_cameras(max_test=10):
        """Lista todas as câmeras disponíveis"""
        print("🔍 Procurando câmeras disponíveis...")
        available = []
        
        for i in range(max_test):
            try:
                # Tenta diferentes backends
                for backend in [cv2.CAP_DSHOW, cv2.CAP_MSMF, cv2.CAP_ANY]:
                    cap = cv2.VideoCapture(i, backend)
                    if cap.isOpened():
                        ret, frame = cap.read()
                        if ret and frame is not None:
                            h, w = frame.shape[:2]
                            available.append({
                                'id': i,
                                'resolution': f"{w}x{h}",
                                'backend': backend
                            })
                            print(f"  ✅ ID {i}: {w}x{h}")
                            cap.release()
                            break
                    cap.release()
            except Exception as e:
                pass
        
        if available:
            print(f"\n✅ Total de câmeras encontradas: {len(available)}")
            return available
        else:
            print("\n❌ Nenhuma câmera encontrada")
            return []
    
    def start(self):
        """Inicia a captura de frames em thread separada"""
        if self.is_running:
            print("⚠️  Câmera já está rodando")
            return self
        
        if not self.cap or not self.cap.isOpened():
            raise ValueError("Câmera não está aberta. Não é possível iniciar.")
        
        self.is_running = True
        self.thread = threading.Thread(target=self._capture_loop, daemon=True)
        self.thread.start()
        print("✅ Captura iniciada em thread separada")
        return self
    
    def _capture_loop(self):
        """Loop de captura (roda em thread separada)"""
        consecutive_failures = 0
        max_failures = 30  # 30 falhas consecutivas = ~1 segundo
        
        try:
            while self.is_running:
                ret, frame = self.cap.read()
                
                if ret and frame is not None:
                    consecutive_failures = 0  # Reset contador
                    
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
                else:
                    consecutive_failures += 1
                    if consecutive_failures >= max_failures:
                        print(f"❌ Erro: Muitas falhas consecutivas na leitura da câmera")
                        self.is_running = False
                        break
                
                # Controla FPS
                time.sleep(1 / self.fps)
        except Exception as e:
            print(f"❌ Erro no loop de captura: {e}")
            self.is_running = False
    
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
        print("⏹️  Parando câmera...")
        self.is_running = False
        
        # CRÍTICO: Aguardar thread terminar ANTES de liberar recursos
        if hasattr(self, 'thread') and self.thread and self.thread.is_alive():
            self.thread.join(timeout=3.0)
            if self.thread.is_alive():
                print("⚠️  Thread de captura não parou a tempo")
        
        # Liberar recursos OpenCV apenas DEPOIS que thread parou
        if hasattr(self, 'cap') and self.cap:
            try:
                self.cap.release()
            except Exception as e:
                print(f"⚠️  Erro ao liberar câmera: {e}")
        
        print("✅ Câmera liberada")
    
    def __enter__(self):
        return self.start()
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.stop()
    
    def __del__(self):
        """Destrutor - garante que recursos sejam liberados"""
        try:
            if hasattr(self, 'is_running') and self.is_running:
                self.stop()
        except Exception:
            # Ignora erros durante destruição (comum quando Python está finalizando)
            pass


if __name__ == "__main__":
    # Primeiro, lista câmeras disponíveis
    print("=" * 60)
    print("TESTE DO CAMERA MANAGER")
    print("=" * 60)
    
    cameras = CameraManager.list_cameras()
    
    if not cameras:
        print("\n❌ Nenhuma câmera disponível. Encerrando.")
        exit(1)
    
    # Usa a primeira câmera disponível
    camera_id = cameras[0]['id']
    print(f"\n🎥 Usando câmera ID: {camera_id}")
    
    try:
        camera = CameraManager(src=camera_id, size=DEFAULT_SIZE, fps=DEFAULT_FPS)
        camera.start()
        
        print("\n✅ Sistema iniciado!")
        print("📹 Mostrando vídeo. Pressione 'q' para sair.")
        print("-" * 60)
        
        frame_count = 0
        start_time = time.time()
        
        while True:
            frame = camera.get_frame()
            
            if frame is not None:
                frame_count += 1
                elapsed = time.time() - start_time
                fps = frame_count / elapsed if elapsed > 0 else 0
                
                # Adiciona informações no frame
                cv2.putText(frame, f"Camera ID: {camera_id}", (10, 30), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                cv2.putText(frame, f"FPS: {fps:.1f}", (10, 60), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                cv2.putText(frame, f"Resolucao: {frame.shape[1]}x{frame.shape[0]}", (10, 90), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                
                cv2.imshow("Camera Manager Test", frame)
                
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    print("\n👋 Encerrando por comando do usuário")
                    break
            else:
                print("⏳ Aguardando frame...")
                time.sleep(0.1)
                
    except ValueError as e:
        print(f"\n{e}")
    except KeyboardInterrupt:
        print("\n👋 Encerrando por Ctrl+C")
    finally:
        if 'camera' in locals():
            camera.stop()
        cv2.destroyAllWindows()
        print("\n✅ Programa finalizado")