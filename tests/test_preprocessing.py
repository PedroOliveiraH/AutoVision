from io import BytesIO
from PIL import Image
import pytest
from src.preprocessing import load_image, crop_percent, estimate_color


def test_redimensionamento_proporcional():
    buf = BytesIO()
    Image.new("RGB", (1600, 800), "white").save(buf, "PNG")
    image = load_image(buf.getvalue(), max_side=1000)
    assert image.size == (1000, 500)


def test_crop_pixels():
    image = Image.new("RGB", (1000, 500), "red")
    crop, rect = crop_percent(image, 10, 20, 90, 80)
    assert rect == (100, 100, 900, 400)
    assert crop.size == (800, 300)


def test_entrada_invalida():
    with pytest.raises(ValueError):
        load_image(b"isso nao e uma imagem")


def test_estimativa_cor_basica():
    image = Image.new("RGB", (100, 100), (255, 0, 0))
    assert estimate_color(image) == "vermelho"
