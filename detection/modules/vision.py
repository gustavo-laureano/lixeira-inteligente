from ultralytics import YOLO
from modules import config
from modules import camera_manager as cm
from modules import model_loader
import cv2
import numpy as np
import torch


def YoloTracker():
    cam = cm.CameraManager(
        src=config.CAMERA_ID,
        size=config.CAMERA_WIDTH,
        fps=config.CAMERA_FPS

    )
    cam.start()

    model = model_loader.load_yolo_model(config.MODEL_PATH) 



    while True:
        frame = cam.get_frame()
        results = model.track(frame, persist=True, tracker="bytetrack.yaml", verbose=False) 

        for result in results:
            boxes = result.boxes

            for box in boxes:
                track_id = box.id
                cls_id = int(box.cls)
                conf = float(box.conf)
                if isinstance(box.xyxy, torch.Tensor):
                    xyxy = box.xyxy.detach().cpu().numpy()
                # Agora deve ser numpy array ou lista
                xyxy = np.asarray(xyxy)
                # Remover dimensões extras: (1,4) -> (4,)
                xyxy = np.squeeze(xyxy)
                if xyxy.ndim != 1 or xyxy.size < 4:
                    raise ValueError(f"Formato inesperado para xyxy: shape={xyxy.shape}, value={xyxy}")
                x1, y1, x2, y2 = map(int, xyxy[:4])

                class_name = model.names[cls_id]

                print(f"ID: {track_id}, Classe: {class_name}, Confiança: {conf:.2f}, Caixa: ({x1}, {y1}), ({x2}, {y2})")

                cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
                cv2.putText(frame, f"{class_name} ID:{track_id} {conf:.2f}", (x1, y1 - 10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
        cv2.imshow("Rastreamento YOLO", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    cam.stop()

YoloTracker()
cv2.destroyAllWindows()
