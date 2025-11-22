import torch
from ultralytics import YOLO
from modules import config

def load_yolo_model(model_name: str | None = None):
    if model_name is None:
        model_name = config.MODEL_PATH

    # mantem compatibilidade com serialização (se necessário)
    try:
        torch.serialization.add_safe_globals([torch.nn.modules.container.Sequential])
    except Exception:
        pass

    print(f"📦 Carregando modelo: {model_name}")
    model = YOLO(model_name)

    # --- Confidence ---
    conf_value = getattr(config, "CONFIDENCE_THRESHOLD", None)
    if conf_value is not None:
        try:
            conf_value = float(conf_value)
            if not (0.0 <= conf_value <= 1.0):
                raise ValueError("CONFIDENCE_THRESHOLD deve estar entre 0.0 e 1.0")
            # atribui no objeto (algumas versões usam model.conf)
            try:
                model.conf = conf_value
            except Exception:
                pass
        except Exception as e:
            raise RuntimeError(f"Valor inválido para CONFIDENCE_THRESHOLD: {e}")

    # --- Classes ---
    target_classes = getattr(config, "TARGET_CLASSES", None)
    classes_to_set = None
    if target_classes is not None:
        # aceita int, str ou iteráveis
        if isinstance(target_classes, (int, str)):
            target_classes = [target_classes]

        if all(isinstance(c, str) for c in target_classes):
            # converte nomes -> índices usando model.names
            name_to_idx = {v: k for k, v in model.names.items()}
            missing = [c for c in target_classes if c not in name_to_idx]
            if missing:
                raise ValueError(f"Classes não encontradas no modelo: {missing}. Disponíveis: {list(model.names.values())}")
            classes_to_set = [name_to_idx[c] for c in target_classes]
        elif all(isinstance(c, int) for c in target_classes):
            # valida range
            if min(target_classes) < 0 or max(target_classes) >= len(model.names):
                raise ValueError(f"Índices em TARGET_CLASSES fora do intervalo válido [0, {len(model.names)-1}]")
            classes_to_set = list(target_classes)
        else:
            raise ValueError("TARGET_CLASSES deve ser None, lista de ints (índices) ou lista de strings (nomes).")

        try:
            model.classes = classes_to_set
        except Exception:
            pass

    # Algumas versões do ultralytics usam model.overrides
    try:
        overrides = {}
        if conf_value is not None:
            overrides["conf"] = conf_value
        if classes_to_set is not None:
            overrides["classes"] = classes_to_set
        if overrides and hasattr(model, "overrides"):
            model.overrides.update(overrides)
    except Exception:
        pass

    print("✅ Modelo carregado")
    print(f"📊 Todas as classes (index:name): {model.names}")
    print(f"🔎 Confidence aplicado: {getattr(model, 'conf', conf_value)}")
    print(f"🎯 Classes aplicadas (índices): {getattr(model, 'classes', classes_to_set)}")

    return model

if __name__ == "__main__":
    m = load_yolo_model()
    # exemplo de inferência usando os valores já aplicados:
    # results = m("img.jpg")
    # ou forçar na chamada (ignora config se desejar):
    # results = m("img.jpg", conf=0.5, classes=[0,2])