import tkinter as tk
from tkinter import ttk, messagebox
import cv2
from PIL import Image, ImageTk
import threading
import time


class CameraSelector:
    """Janela de seleção de câmera com preview"""
    
    def __init__(self):
        self.selected_camera = None
        self.available_cameras = []
        self.preview_active = False
        self.preview_thread = None
        self.cap = None
        
        # Cria janela principal
        self.root = tk.Tk()
        self.root.title("🎥 Seleção de Câmera - Lixeira Inteligente")
        self.root.geometry("800x600")
        self.root.resizable(False, False)
        
        # Configura estilo
        style = ttk.Style()
        style.theme_use('clam')
        
        self._create_widgets()
        self._scan_cameras()
    
    def _create_widgets(self):
        """Cria os widgets da interface"""
        
        # Frame principal
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Título
        title = ttk.Label(
            main_frame, 
            text="🎥 Selecione a Câmera",
            font=("Arial", 18, "bold")
        )
        title.pack(pady=(0, 20))
        
        # Frame de seleção
        selection_frame = ttk.LabelFrame(main_frame, text="Câmeras Disponíveis", padding="10")
        selection_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Lista de câmeras
        self.camera_listbox = tk.Listbox(
            selection_frame,
            height=5,
            font=("Consolas", 10),
            selectmode=tk.SINGLE
        )
        self.camera_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))
        self.camera_listbox.bind('<<ListboxSelect>>', self._on_camera_select)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(selection_frame, orient=tk.VERTICAL, command=self.camera_listbox.yview)
        scrollbar.pack(side=tk.LEFT, fill=tk.Y)
        self.camera_listbox.config(yscrollcommand=scrollbar.set)
        
        # Frame de preview
        preview_frame = ttk.LabelFrame(main_frame, text="Preview da Câmera", padding="10")
        preview_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # Label para mostrar o vídeo
        self.video_label = ttk.Label(preview_frame, text="Selecione uma câmera para ver o preview", 
                                     background="black", foreground="white")
        self.video_label.pack(fill=tk.BOTH, expand=True)
        
        # Frame de botões
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X)
        
        # Botão Atualizar
        self.btn_refresh = ttk.Button(
            button_frame,
            text="🔄 Atualizar Lista",
            command=self._scan_cameras
        )
        self.btn_refresh.pack(side=tk.LEFT, padx=(0, 5))
        
        # Botão Testar
        self.btn_test = ttk.Button(
            button_frame,
            text="🧪 Testar Câmera",
            command=self._test_camera,
            state=tk.DISABLED
        )
        self.btn_test.pack(side=tk.LEFT, padx=(0, 5))
        
        # Espaçador
        ttk.Label(button_frame).pack(side=tk.LEFT, expand=True)
        
        # Botão Cancelar
        self.btn_cancel = ttk.Button(
            button_frame,
            text="❌ Cancelar",
            command=self._on_cancel
        )
        self.btn_cancel.pack(side=tk.LEFT, padx=(0, 5))
        
        # Botão Confirmar
        self.btn_confirm = ttk.Button(
            button_frame,
            text="✅ Confirmar",
            command=self._on_confirm,
            state=tk.DISABLED
        )
        self.btn_confirm.pack(side=tk.LEFT)
        
        # Status bar
        self.status_var = tk.StringVar(value="Procurando câmeras...")
        status_bar = ttk.Label(self.root, textvariable=self.status_var, relief=tk.SUNKEN, anchor=tk.W)
        status_bar.pack(side=tk.BOTTOM, fill=tk.X)
    
    def _scan_cameras(self):
        """Procura câmeras disponíveis no sistema"""
        self.btn_refresh.config(state=tk.DISABLED)
        self.status_var.set("🔍 Procurando câmeras...")
        self.root.update()
        
        # Limpa lista anterior
        self.camera_listbox.delete(0, tk.END)
        self.available_cameras = []
        
        # Procura câmeras (ID 0 a 9)
        for i in range(10):
            try:
                # Tenta diferentes backends
                for backend_name, backend in [
                    ("DirectShow", cv2.CAP_DSHOW),
                    ("MSMF", cv2.CAP_MSMF),
                    ("Auto", cv2.CAP_ANY)
                ]:
                    cap = cv2.VideoCapture(i, backend)
                    if cap.isOpened():
                        ret, frame = cap.read()
                        if ret and frame is not None:
                            h, w = frame.shape[:2]
                            
                            # Tenta pegar nome da câmera (Windows)
                            name = f"Câmera {i}"
                            
                            camera_info = {
                                'id': i,
                                'name': name,
                                'resolution': f"{w}x{h}",
                                'backend': backend_name,
                                'working': True
                            }
                            
                            self.available_cameras.append(camera_info)
                            
                            # Adiciona à lista
                            display_text = f"ID {i}: {name} [{w}x{h}] ({backend_name})"
                            self.camera_listbox.insert(tk.END, display_text)
                            
                            cap.release()
                            break
                    cap.release()
            except Exception as e:
                pass
        
        # Atualiza status
        if self.available_cameras:
            self.status_var.set(f"✅ {len(self.available_cameras)} câmera(s) encontrada(s)")
        else:
            self.status_var.set("❌ Nenhuma câmera encontrada")
            messagebox.showwarning(
                "Nenhuma câmera",
                "Nenhuma câmera foi encontrada.\n\n"
                "Verifique se:\n"
                "• A câmera está conectada\n"
                "• Drivers estão instalados\n"
                "• Nenhum outro programa está usando a câmera"
            )
        
        self.btn_refresh.config(state=tk.NORMAL)
    
    def _on_camera_select(self, event):
        """Callback quando uma câmera é selecionada"""
        selection = self.camera_listbox.curselection()
        if selection:
            idx = selection[0]
            camera_info = self.available_cameras[idx]
            self.selected_camera = camera_info['id']
            
            self.btn_test.config(state=tk.NORMAL)
            self.btn_confirm.config(state=tk.NORMAL)
            
            # Inicia preview
            self._start_preview()
    
    def _start_preview(self):
        """Inicia preview da câmera selecionada"""
        # Para preview anterior se existir
        self._stop_preview()
        
        self.preview_active = True
        self.preview_thread = threading.Thread(target=self._preview_loop, daemon=True)
        self.preview_thread.start()
    
    def _stop_preview(self):
        """Para o preview da câmera"""
        self.preview_active = False
        if self.preview_thread:
            self.preview_thread.join(timeout=1.0)
        if self.cap:
            self.cap.release()
            self.cap = None
    
    def _preview_loop(self):
        """Loop de preview (roda em thread separada)"""
        try:
            # Abre câmera
            self.cap = cv2.VideoCapture(self.selected_camera, cv2.CAP_DSHOW)
            
            if not self.cap.isOpened():
                self.root.after(0, lambda: self.video_label.config(
                    text="❌ Erro ao abrir câmera",
                    background="red"
                ))
                return
            
            while self.preview_active:
                ret, frame = self.cap.read()
                
                if ret and frame is not None:
                    # Redimensiona para caber na janela (mantém proporção)
                    h, w = frame.shape[:2]
                    max_width = 760
                    max_height = 400
                    
                    scale = min(max_width / w, max_height / h)
                    new_w = int(w * scale)
                    new_h = int(h * scale)
                    
                    frame = cv2.resize(frame, (new_w, new_h))
                    
                    # Converte BGR para RGB
                    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    
                    # Converte para ImageTk
                    img = Image.fromarray(frame_rgb)
                    imgtk = ImageTk.PhotoImage(image=img)
                    
                    # Atualiza label (na thread principal)
                    self.root.after(0, lambda img=imgtk: self._update_preview(img))
                
                time.sleep(0.033)  # ~30 FPS
                
        except Exception as e:
            self.root.after(0, lambda: self.video_label.config(
                text=f"❌ Erro no preview: {e}",
                background="red"
            ))
    
    def _update_preview(self, imgtk):
        """Atualiza a imagem do preview (thread-safe)"""
        self.video_label.config(image=imgtk, text="")
        self.video_label.image = imgtk  # Mantém referência
    
    def _test_camera(self):
        """Abre janela de teste da câmera"""
        if self.selected_camera is None:
            return
        
        # Para preview
        self._stop_preview()
        
        # Abre janela cv2
        messagebox.showinfo(
            "Teste de Câmera",
            f"Abrindo câmera {self.selected_camera} em janela separada.\n\n"
            "Pressione 'q' para fechar a janela de teste."
        )
        
        cap = cv2.VideoCapture(self.selected_camera, cv2.CAP_DSHOW)
        
        if not cap.isOpened():
            messagebox.showerror("Erro", "Não foi possível abrir a câmera")
            return
        
        try:
            while True:
                ret, frame = cap.read()
                if ret:
                    # Adiciona info
                    cv2.putText(frame, f"Camera ID: {self.selected_camera}", (10, 30),
                               cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
                    cv2.putText(frame, "Pressione 'q' para sair", (10, 70),
                               cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
                    
                    cv2.imshow(f"Teste - Camera {self.selected_camera}", frame)
                    
                    if cv2.waitKey(1) & 0xFF == ord('q'):
                        break
        finally:
            cap.release()
            cv2.destroyAllWindows()
            
            # Reinicia preview
            self._start_preview()
    
    def _on_confirm(self):
        """Confirma seleção da câmera"""
        if self.selected_camera is not None:
            self._stop_preview()
            self.root.destroy()
    
    def _on_cancel(self):
        """Cancela seleção"""
        self.selected_camera = None
        self._stop_preview()
        self.root.destroy()
    
    def show(self):
        """Mostra a janela e retorna a câmera selecionada"""
        # Centraliza janela
        self.root.update_idletasks()
        x = (self.root.winfo_screenwidth() // 2) - (self.root.winfo_width() // 2)
        y = (self.root.winfo_screenheight() // 2) - (self.root.winfo_height() // 2)
        self.root.geometry(f"+{x}+{y}")
        
        # Evento de fechamento
        self.root.protocol("WM_DELETE_WINDOW", self._on_cancel)
        
        # Mostra janela
        self.root.mainloop()
        
        return self.selected_camera


def select_camera():
    """
    Função helper para seleção de câmera
    
    Returns:
        int or None: ID da câmera selecionada ou None se cancelado
    """
    selector = CameraSelector()
    camera_id = selector.show()
    
    if camera_id is not None:
        print(f"✅ Câmera selecionada: ID {camera_id}")
    else:
        print("❌ Seleção cancelada")
    
    return camera_id


if __name__ == "__main__":
    # Teste standalone
    print("=" * 60)
    print("SELETOR DE CÂMERA")
    print("=" * 60)
    
    camera_id = select_camera()
    
    if camera_id is not None:
        print(f"\n✅ Você pode usar: CameraManager(src={camera_id})")
    else:
        print("\n❌ Nenhuma câmera selecionada")
