#!/usr/bin/env python3
"""
Script de teste para a câmera
Útil para verificar se a câmera está funcionando corretamente
"""

import cv2
import sys

def test_camera(device=0, width=640, height=480):
    """Testa a câmera"""
    print(f"Testando câmera (device={device}, resolução={width}x{height})")
    print("Pressione 'q' para sair ou 's' para salvar uma imagem")
    
    # Abre câmera
    cap = cv2.VideoCapture(device)
    
    if not cap.isOpened():
        print("❌ Erro: Não foi possível abrir a câmera!")
        print("\nTente:")
        print("  - Verificar se a câmera está conectada")
        print("  - Usar outro device: python test_camera.py 1")
        print("  - Verificar permissões: sudo chmod 666 /dev/video*")
        return False
    
    # Configura resolução
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
    
    # Verifica configuração
    actual_width = cap.get(cv2.CAP_PROP_FRAME_WIDTH)
    actual_height = cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
    fps = cap.get(cv2.CAP_PROP_FPS)
    
    print(f"✅ Câmera aberta!")
    print(f"   Resolução: {int(actual_width)}x{int(actual_height)}")
    print(f"   FPS: {fps}")
    
    frame_count = 0
    
    try:
        while True:
            ret, frame = cap.read()
            
            if not ret:
                print("❌ Erro ao capturar frame!")
                break
            
            frame_count += 1
            
            # Adiciona informações no frame
            cv2.putText(frame, f"Frame: {frame_count}", (10, 30),
                       cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
            cv2.putText(frame, "Pressione 'q' para sair", (10, 70),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
            cv2.putText(frame, "Pressione 's' para salvar", (10, 100),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
            
            # Mostra frame
            cv2.imshow('Teste de Camera', frame)
            
            # Verifica teclas
            key = cv2.waitKey(1) & 0xFF
            
            if key == ord('q'):
                print("Encerrando...")
                break
            elif key == ord('s'):
                filename = f"test_frame_{frame_count}.jpg"
                cv2.imwrite(filename, frame)
                print(f"✅ Imagem salva: {filename}")
    
    except KeyboardInterrupt:
        print("\nInterrompido pelo usuário")
    
    finally:
        cap.release()
        cv2.destroyAllWindows()
        print(f"\n✅ Total de frames capturados: {frame_count}")
        return True

if __name__ == "__main__":
    device = int(sys.argv[1]) if len(sys.argv) > 1 else 0
    width = int(sys.argv[2]) if len(sys.argv) > 2 else 640
    height = int(sys.argv[3]) if len(sys.argv) > 3 else 480
    
    success = test_camera(device, width, height)
    sys.exit(0 if success else 1)
