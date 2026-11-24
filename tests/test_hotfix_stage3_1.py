"""Hotfix Etapa 3.1: mensagens corretas e regressao de competicao Porsche.

Testes de logica e de rotulos, NAO mensuram a precisao do CLIP com fotos.
"""
from PIL import Image

from src.recognition import (
    CANDIDATES, DISTRACTOR_LABELS, classify_with_alternatives,
    decide_with_alternatives,
)


def test_porsche_991_nao_concorre_no_ranking_geral():
    assert "porsche-911-gt3-rs-2010" in CANDIDATES
    assert "fora-porsche-991" not in DISTRACTOR_LABELS
    assert "fora-beetle-a5" in DISTRACTOR_LABELS


def test_classificador_nao_envia_prompt_991_para_clip(monkeypatch):
    class FakeModel:
        def __call__(self, image, candidate_labels, hypothesis_template):
            assert image.size == (10, 10)
            assert any("997.2" in s for s in candidate_labels)
            assert not any("991" in s for s in candidate_labels)
            assert any("Beetle A5" in s for s in candidate_labels)
            return [{"label": candidate_labels[0], "score": 0.90},
                    {"label": candidate_labels[1], "score": 0.10}]
    monkeypatch.setattr("src.recognition._get_classifier", lambda: FakeModel())
    results = classify_with_alternatives(Image.new("RGB", (10, 10)))
    assert len(results) == 2


def test_modo_manual_desconhecido_nao_afirma_que_ha_carro():
    result = [{"slug": "fora-gol", "score": 0.9},
              {"slug": "volkswagen-fusca", "score": 0.05}]
    slug, message = decide_with_alternatives(result, manual_mode=True)
    assert slug is None
    assert "não foi verificado" in message
    assert "Há um automóvel" not in message


def test_modo_manual_ambiguidade_nao_afirma_deteccao():
    result = [{"slug": "volkswagen-fusca", "score": 0.50},
              {"slug": "fora-gol", "score": 0.45}]
    slug, message = decide_with_alternatives(result, manual_mode=True)
    assert slug is None
    assert "não confirma" in message


def test_modo_manual_sugestao_nao_afirma_deteccao():
    result = [{"slug": "volkswagen-fusca", "score": 0.95},
              {"slug": "fora-gol", "score": 0.02}]
    slug, message = decide_with_alternatives(result, manual_mode=True)
    assert slug == "volkswagen-fusca"
    assert "não foi confirmada" in message


def test_modo_automatico_contraste_nao_afirma_identidade():
    result = [{"slug": "fora-gol", "score": 0.95},
              {"slug": "fiat-uno", "score": 0.02}]
    slug, message = decide_with_alternatives(result)
    assert slug is None
    assert "O YOLO detectou uma região compatível" in message
