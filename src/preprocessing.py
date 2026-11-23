"""Aquisição, redimensionamento proporcional e análise exploratória de cor."""
from collections import Counter
from io import BytesIO
import cv2
import numpy as np
from PIL import Image, ImageOps, UnidentifiedImageError

MAX_IMAGE_BYTES = 12 * 1024 * 1024
Image.MAX_IMAGE_PIXELS = 40_000_000


def load_image(data: bytes, max_side: int = 1000) -> Image.Image:
    if not data or len(data) > MAX_IMAGE_BYTES:
        raise ValueError("A imagem está vazia ou ultrapassa 12 MB.")
    try:
        with Image.open(BytesIO(data)) as original:
            img = ImageOps.exif_transpose(original).convert("RGB")
    except (UnidentifiedImageError, OSError, ValueError) as exc:
        raise ValueError("Arquivo incompatível ou imagem inválida.") from exc

    w, h = img.size
    if w == 0 or h == 0:
        raise ValueError("Imagem com dimensões inválidas.")
    scale = min(1.0, max_side / max(w, h))
    if scale < 1:
        new_size = (max(1, round(w * scale)), max(1, round(h * scale)))
        # Operação 1: redimensionamento proporcional.
        arr = cv2.resize(np.asarray(img), new_size, interpolation=cv2.INTER_AREA)
        img = Image.fromarray(arr)
    return img


def crop_percent(img: Image.Image, left: int, top: int, right: int, bottom: int):
    if not (0 <= left < right <= 100 and 0 <= top < bottom <= 100):
        raise ValueError("A região deve ter esquerda < direita e topo < base.")
    w, h = img.size
    rect = (int(w * left / 100), int(h * top / 100),
            max(1, int(w * right / 100)), max(1, int(h * bottom / 100)))
    return img.crop(rect), rect


def estimate_color(img: Image.Image) -> str:
    """Estimativa NÃO confiável de cor: não há segmentação real da carroceria."""
    rgb = np.asarray(img.convert("RGB"))
    h, w = rgb.shape[:2]
    # Usa região central; fundo/reflexos podem dominar a estimativa.
    rgb = rgb[h//5:max(h//5 + 1, 4*h//5), w//5:max(w//5 + 1, 4*w//5)]
    # Operação 2: suavização para reduzir ruído de pixel.
    blurred = cv2.GaussianBlur(rgb, (5, 5), 0)
    # Operação 3: conversão RGB -> HSV para avaliação de cor.
    hsv = cv2.cvtColor(blurred, cv2.COLOR_RGB2HSV)
    hsv = hsv.reshape(-1, 3)
    if len(hsv) > 3000:
        hsv = hsv[::max(1, len(hsv)//3000)]
    labels = []
    for hue, sat, val in hsv:
        h, s, v = int(hue), int(sat), int(val)
        if v < 55:
            c = "preto/escuro"
        elif s < 35 and v > 195:
            c = "branco/claro"
        elif s < 45:
            c = "cinza/prateado"
        elif h < 10 or h >= 170:
            c = "vermelho"
        elif h < 20:
            c = "laranja/marrom"
        elif h < 35:
            c = "amarelo"
        elif h < 85:
            c = "verde"
        elif h < 100:
            c = "ciano"
        elif h < 135:
            c = "azul"
        else:
            c = "roxo/rosa"
        labels.append(c)
    return Counter(labels).most_common(1)[0][0] if labels else "indeterminada"
