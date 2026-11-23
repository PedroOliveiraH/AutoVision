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
