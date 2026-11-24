"""Testes locais, sem acesso a pesos/Internet. Não avaliam a precisão da IA."""
from PIL import Image

from src.vehicle_detection import normalize_boxes, detect_car_boxes
from src.visualization import annotate_detections
from src.recognition import DISTRACTOR_LABELS, decide_with_alternatives
from src.preprocessing import crop_percent, estimate_color


def test_multiplos_veiculos_ordenados_por_confianca():
    positions = [[15, 20, 115, 100], [130, 25, 210, 120]]
    confs = [0.60, 0.94]
    boxes = normalize_boxes(positions, confs, (220, 140))
    assert len(boxes) == 2
    assert boxes[0] == {"box": (130, 25, 210, 120), "confidence": 0.94}
    assert boxes[1]["box"] == (15, 20, 115, 100)


def test_normalizacao_limita_coordenadas_e_remove_caixas_invalidas():
    boxes = normalize_boxes([[-30, -5, 250, 300], [45, 45, 45, 65]],
                            [0.7, 0.9], (160, 90))
    assert len(boxes) == 1
    assert boxes[0]["box"] == (0, 0, 160, 90)


def test_sem_caixas_retorna_lista_vazia():
    assert normalize_boxes([], [], (120, 70)) == []


def test_multiplas_caixas_sobrepostas_sem_mudar_imagem_original():
    image = Image.new("RGB", (260, 150), "white")
    boxes = [
        {"box": (0, 0, 100, 60), "confidence": 0.91},
        {"box": (80, 40, 180, 110), "confidence": 0.45},
    ]
    result = annotate_detections(image, boxes, selected_index=1, offset=(25, 15))
    assert result.size == image.size
    assert result.getpixel((25, 15)) != (255, 255, 255)
    assert result.getpixel((105, 55)) != (255, 255, 255)
    assert image.getpixel((25, 15)) == (255, 255, 255)


def test_descricao_de_contrastes_de_fusca_moderno():
    assert "fora-new-beetle" in DISTRACTOR_LABELS
    assert "fora-beetle-a5" in DISTRACTOR_LABELS
    assert "fora-porsche-991" not in DISTRACTOR_LABELS
    results = [{"slug": "fora-beetle-a5", "score": 0.80},
               {"slug": "volkswagen-fusca", "score": 0.20}]
    slug, message = decide_with_alternatives(results)
    assert slug is None
    assert "não encontrou correspondência segura" in message


def test_amostra_manual_da_pintura_vermelha():
    image = Image.new("RGB", (100, 100), "black")
    # No interior do carro, a pequena região pintada ocupa somente o canto superior.
    from PIL import ImageDraw
    ImageDraw.Draw(image).rectangle((10, 10, 40, 40), fill="red")
    patch, rect = crop_percent(image, 12, 12, 38, 38)
    assert patch.size == (26, 26)
    assert estimate_color(patch) == "vermelho"


def test_detector_pode_ser_simulado_sem_baixar_pesos(monkeypatch):
    class FakeTensor:
        def __init__(self, arr): self.arr = arr
        def cpu(self): return self
        def tolist(self): return self.arr

    class FakeBoxes:
        conf = FakeTensor([0.82, 0.67])
        xyxy = FakeTensor([[5, 10, 70, 60], [80, 10, 150, 65]])
        def __len__(self): return 2

    class FakeResult:
        boxes = FakeBoxes()

    class FakeDetector:
        def predict(self, **kwargs):
            assert kwargs["classes"] == [2]
            assert kwargs["imgsz"] == 640
            return [FakeResult()]

    import src.vehicle_detection as detection
    monkeypatch.setattr(detection, "_get_detector", lambda: FakeDetector())
    image = Image.new("RGB", (180, 90), "white")
    found = detect_car_boxes(image)
    assert len(found) == 2
    assert found[1]["confidence"] == 0.67
