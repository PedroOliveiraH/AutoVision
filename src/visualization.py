"""Sobreposição gráfica e mapeamento de coordenadas."""
from PIL import Image, ImageDraw, ImageFont


def annotate(image: Image.Image, rect, title: str) -> Image.Image:
    base = image.convert("RGBA")
    w, h = base.size
    # Camada independente com transparência: composição alpha.
    layer = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    draw = ImageDraw.Draw(layer)
    if rect:
        draw.rectangle(rect, outline=(38, 210, 138, 255), width=max(2, w // 250))
    label_height = min(48, max(30, h // 10))
    draw.rectangle((0, 0, w, label_height), fill=(3, 26, 42, 185))
    draw.text((12, max(5, label_height // 3)), title[:85], fill=(255, 255, 255, 255))
    return Image.alpha_composite(base, layer).convert("RGB")


def annotate_detections(image: Image.Image, detections, selected_index=None, offset=(0, 0)) -> Image.Image:
    """Desenha todas as caixas e marca a escolhida com outra cor.

    As coordenadas são relativas à ROI; offset as transforma para a imagem inteira.
    """
    canvas = image.convert("RGBA")
    w, h = canvas.size
    layer = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    draw = ImageDraw.Draw(layer)
    off_x, off_y = offset
    thickness = max(3, w // 240)
    for index, found in enumerate(detections):
        x1, y1, x2, y2 = found["box"]
        rect = (x1 + off_x, y1 + off_y, x2 + off_x, y2 + off_y)
        color = (255, 205, 40, 255) if index == selected_index else (25, 224, 155, 255)
        draw.rectangle(rect, outline=color, width=thickness)
        text = f"{index + 1}  {found['confidence']:.0%}"
        tx, ty = max(0, rect[0]), max(0, rect[1] - 22)
        text_box = draw.textbbox((tx + 4, ty + 3), text)
        draw.rectangle((tx, ty, min(w, text_box[2] + 5), min(h, text_box[3] + 4)), fill=(0, 25, 33, 220))
        draw.text((tx + 4, ty + 3), text, fill=color)
    return Image.alpha_composite(canvas, layer).convert("RGB")
