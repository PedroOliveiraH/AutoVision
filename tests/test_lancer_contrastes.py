"""Correção de rótulos para o Lancer (sem pesos CLIP e sem Internet).

Estes testes verificam a LOGICA, nao a capacidade real do CLIP em fotografias.
"""
from PIL import Image

from src.recognition import (
    CANDIDATES, DISTRACTOR_LABELS,
    classify_with_alternatives, decide_with_alternatives,
)


def test_catalogo_permanece_com_cinco_modelos_e_porsche_997():
    assert len(CANDIDATES) == 5
    assert "porsche-911-gt3-rs-2010" in CANDIDATES
    assert "fora-lancer-evo-x" not in CANDIDATES
    assert "fora-porsche-991" not in DISTRACTOR_LABELS


def test_descricoes_do_lancer_e_seda_esportivo_sao_contrastes():
    assert "Mitsubishi Lancer Evolution X" in DISTRACTOR_LABELS["fora-lancer-evo-x"]
    assert "four door" in DISTRACTOR_LABELS["fora-seda-esportivo"]


def test_clip_recebe_os_novos_rotulos(monkeypatch):
    class ClassifierFake:
        def __call__(self, image, candidate_labels, hypothesis_template):
            assert image.size == (16, 16)
            assert hypothesis_template == "This is a photo of {}."
            assert any("Mitsubishi Lancer Evolution X" in x for x in candidate_labels)
            assert any("four door sports sedan" in x for x in candidate_labels)
            assert any("997.2" in x for x in candidate_labels)
            return [
                {"label": DISTRACTOR_LABELS["fora-lancer-evo-x"], "score": 0.79},
                {"label": CANDIDATES["porsche-911-gt3-rs-2010"], "score": 0.19},
            ]

    monkeypatch.setattr("src.recognition._get_classifier", lambda: ClassifierFake())
    results = classify_with_alternatives(Image.new("RGB", (16, 16)))
    assert [x["slug"] for x in results] == ["fora-lancer-evo-x", "porsche-911-gt3-rs-2010"]


def test_lancer_classificado_como_contraste_e_rejeitado_em_modo_manual():
    results = [
        {"slug": "fora-lancer-evo-x", "score": 0.79},
        {"slug": "porsche-911-gt3-rs-2010", "score": 0.19},
    ]
    slug, message = decide_with_alternatives(results, manual_mode=True)
    assert slug is None
    assert "não foi verificado" in message


def test_porsche_correto_ainda_pode_ser_aceito():
    results = [
        {"slug": "porsche-911-gt3-rs-2010", "score": 0.88},
        {"slug": "fora-lancer-evo-x", "score": 0.06},
        {"slug": "fora-seda-esportivo", "score": 0.03},
    ]
    slug, _ = decide_with_alternatives(results)
    assert slug == "porsche-911-gt3-rs-2010"


def test_margem_apertada_continua_inconclusiva():
    results = [
        {"slug": "porsche-911-gt3-rs-2010", "score": 0.57},
        {"slug": "fora-lancer-evo-x", "score": 0.49},
    ]
    slug, _ = decide_with_alternatives(results)
    assert slug is None
