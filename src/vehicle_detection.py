"""Detecção de todos os automóveis com YOLO11n (classe COCO 2: car).

O reconhecimento do modelo é tarefa SEPARADA do CLIP. Uma caixa pode
corresponder a outro veículo, e veículos reais podem não ser detectados.
"""
from functools import lru_cache

import cv2
import numpy as np
from PIL import Image


@lru_cache(maxsize=1)
def _get_detector():
    from ultralytics import YOLO
    return YOLO("yolo11n.pt")


def normalize_boxes(positions, confidences, size, max_results=15):
    """Converte resultados do detector em caixas válidas, ordenadas por confiança.

    Função pura para teste sem carregar pesos do YOLO.
    """
    width, height = size
    if width <= 0 or height <= 0:
        raise ValueError("Dimensões de imagem inválidas.")
    if len(positions) != len(confidences):
        raise ValueError("Número de caixas e confianças incompatível.")
    detections = []
    for position, confidence in zip(positions, confidences):
        if len(position) != 4:
            continue
        x1, y1, x2, y2 = (int(round(float(v))) for v in position)
        x1, y1 = max(0, min(width, x1)), max(0, min(height, y1))
        x2, y2 = max(0, min(width, x2)), max(0, min(height, y2))
        if x2 <= x1 or y2 <= y1:
            continue
        detections.append({"box": (x1, y1, x2, y2), "confidence": float(confidence)})
    detections.sort(key=lambda item: item["confidence"], reverse=True)
    return detections[:max_results]


def detect_car_boxes(image: Image.Image, confidence: float = 0.30, image_size: int = 640):
    """Retorna lista de caixas e confiança; pode ser vazia.

    Não seleciona automaticamente qual automóvel o usuário quer analisar.
    """
    if not 0.01 <= confidence <= 1.0:
        raise ValueError("Limiar YOLO deve estar entre 0.01 e 1.0.")
    if image_size not in (480, 640, 960):
        raise ValueError("Tamanho YOLO deve ser 480, 640 ou 960.")
    rgb = np.asarray(image.convert("RGB"))
    bgr = cv2.cvtColor(rgb, cv2.COLOR_RGB2BGR)
    predictions = _get_detector().predict(
        source=bgr,
        classes=[2],  # COCO 'car' — não identifica marca ou modelo
        conf=confidence,
        imgsz=image_size,
        device="cpu",
        verbose=False,
        max_det=20,
    )
    if not predictions or predictions[0].boxes is None or len(predictions[0].boxes) == 0:
        return []
    boxes = predictions[0].boxes
    return normalize_boxes(boxes.xyxy.cpu().tolist(), boxes.conf.cpu().tolist(), image.size)


def best_car_box(image: Image.Image, confidence: float = 0.30):
    """Compatibilidade com a Etapa 2."""
    detected = detect_car_boxes(image, confidence=confidence)
    if not detected:
        return None, None
    return detected[0]["box"], detected[0]["confidence"]
