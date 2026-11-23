"""Detecta automóveis com YOLO antes de tentar reconhecer o modelo.

A detecção pode falhar em carros pequenos, parcialmente ocultos ou imagens
fora da distribuição de treinamento. Isso deve ser informado na avaliação.
"""
from functools import lru_cache

import cv2
import numpy as np
from PIL import Image


@lru_cache(maxsize=1)
def _get_detector():
    from ultralytics import YOLO

    # Modelo nano; no primeiro uso, YOLO baixa yolo11n.pt se necessário.
    return YOLO("yolo11n.pt")


def best_car_box(image: Image.Image, confidence: float = 0.30):
    """Retorna (x1,y1,x2,y2), confiança; ou (None, None).

    COCO classe 2: car. Não confundir detecção genérica com identidade/modelo.
    """
    if not 0.01 <= confidence <= 1:
        raise ValueError("Confiança de detecção fora do intervalo permitido.")

    rgb = np.asarray(image.convert("RGB"))
    bgr = cv2.cvtColor(rgb, cv2.COLOR_RGB2BGR)
    predictions = _get_detector().predict(
        source=bgr,
        classes=[2],  # categoria 'car' do conjunto COCO
        conf=confidence,
        imgsz=640,
        device="cpu",
        verbose=False,
    )
    if not predictions or predictions[0].boxes is None or len(predictions[0].boxes) == 0:
        return None, None

    boxes = predictions[0].boxes
    confidences = boxes.conf.cpu().tolist()
    positions = boxes.xyxy.cpu().tolist()
    idx = max(range(len(confidences)), key=lambda i: confidences[i])
    x1, y1, x2, y2 = (int(round(v)) for v in positions[idx])
    width, height = image.size
    x1, y1 = max(0, x1), max(0, y1)
    x2, y2 = min(width, x2), min(height, y2)
    if x2 <= x1 or y2 <= y1:
        return None, None
    return (x1, y1, x2, y2), float(confidences[idx])
