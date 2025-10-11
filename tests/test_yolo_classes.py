#!/usr/bin/env python3
"""
Lista todas as classes que o modelo YOLO pode detectar
e mostra detecções em tempo real
"""

from ultralytics import YOLO
import cv2
import sys

def list_classes(model_name='yolov8n.pt'):
    """Lista todas as classes do modelo"""
    print(f"Carregando modelo {model_name}...")
    model = YOLO(model_name)
    
    print(f"\n{'='*60}")
    print(f"  Modelo: {model_name}")
    print(f"  Total de classes: {len(model.names)}")
    print(f"{'='*60}\n")
    
    print("Classes disponíveis:\n")
    for idx, name in model.names.items():
        print(f"  {idx:2d} - {name}")
    
    print(f"\n{'='*60}")
    print("\n💡 Classes úteis para lixeira:")
    useful_classes = ['bottle', 'cup', 'bowl', 'wine glass', 'fork', 
                      'knife', 'spoon', 'banana', 'apple', 'orange',
                      'sandwich', 'hot dog', 'pizza', 'donut', 'cake']
    
    for name in useful_classes:
        if name in model.names.values():
            idx = [k for k, v in model.names.items() if v == name][0]
            print(f"  ✅ {idx:2d} - {name}")
    
    print("\n⚠️  Nota: 'can' (lata) NÃO está disponível no COCO dataset")
    print("   Latas são geralmente detectadas como 'bottle'\n")
    
    return model

def test_detection_live(model, device=0):
    """Testa detecção em tempo real"""
    print("\n🎥 Iniciando detecção em tempo real...")
    print("Pressione 'q' para sair\n")
    
    cap = cv2.VideoCapture(device)
    if not cap.isOpened():
        print("❌ Erro ao abrir câmera")
        return
    
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
    
    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            
            # Detecta objetos
            results = model(frame, conf=0.5, verbose=False)
            
            # Desenha detecções
            annotated_frame = results[0].plot()
            
            # Mostra classes detectadas
            boxes = results[0].boxes
            if boxes is not None and len(boxes) > 0:
                detected = []
                for box in boxes:
                    cls = int(box.cls[0])
                    conf = float(box.conf[0])
                    name = model.names[cls]
                    detected.append(f"{name} ({conf:.2f})")
                
                # Mostra na tela
                y_pos = 30
                for det in detected:
                    cv2.putText(annotated_frame, det, (10, y_pos),
                              cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                    y_pos += 30
            
            cv2.imshow('YOLO Detection - Pressione Q para sair', annotated_frame)
            
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
    
    except KeyboardInterrupt:
        print("\nInterrompido")
    finally:
        cap.release()
        cv2.destroyAllWindows()

def test_detection_image(model, image_path):
    """Testa detecção em uma imagem"""
    print(f"\n🖼️  Testando detecção em: {image_path}")
    
    results = model(image_path, conf=0.5)
    
    # Mostra resultados
    boxes = results[0].boxes
    if boxes is None or len(boxes) == 0:
        print("❌ Nenhum objeto detectado")
    else:
        print(f"\n✅ {len(boxes)} objeto(s) detectado(s):\n")
        for box in boxes:
            cls = int(box.cls[0])
            conf = float(box.conf[0])
            name = model.names[cls]
            x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
            print(f"  • {name:15s} - confiança: {conf:.2%} - bbox: [{int(x1)}, {int(y1)}, {int(x2)}, {int(y2)}]")
    
    # Salva imagem com detecções
    output_path = 'detection_result.jpg'
    results[0].save(output_path)
    print(f"\n💾 Resultado salvo em: {output_path}")

if __name__ == "__main__":
    # Lista classes disponíveis
    model = list_classes('yolov8n.pt')
    
    print("\n" + "="*60)
    print("Opções de teste:")
    print("="*60)
    print("1. Testar com câmera ao vivo")
    print("2. Testar com imagem")
    print("3. Apenas listar classes (já feito acima)")
    print("4. Sair")
    
    choice = input("\nEscolha [1-4]: ").strip()
    
    if choice == '1':
        device = int(input("Device da câmera [0]: ").strip() or "0")
        test_detection_live(model, device)
    elif choice == '2':
        image_path = input("Caminho da imagem: ").strip()
        if image_path:
            test_detection_image(model, image_path)
    elif choice == '3':
        print("\n✅ Classes já listadas acima")
    else:
        print("Saindo...")
