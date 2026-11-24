"""Testes da lógica do segundo estágio, sem afirmar precisão em fotos reais."""
from PIL import Image
from src import recognition as r


def test_991_nao_entra_no_ranking_principal():
    assert "fora-porsche-991" not in r.DISTRACTOR_LABELS
    assert len(r.CANDIDATES) == 5
    assert set(r.PORSCHE_GENERATION_DESCRIPTIONS) == {"997", "991"}


def test_comparacao_secundaria_nao_usa_candidatos_de_outras_marcas(monkeypatch):
    class FakeModel:
        def __call__(self, image, candidate_labels, hypothesis_template):
            assert image.size == (16, 16)
            assert hypothesis_template == "This is a photo of {}."
            assert len(candidate_labels) == 4
            assert any("997.2" in x for x in candidate_labels)
            assert any("991.1" in x for x in candidate_labels)
            assert not any("Mitsubishi" in x for x in candidate_labels)
            return [
                {"label": candidate_labels[0], "score": .42},
                {"label": candidate_labels[1], "score": .39},
                {"label": candidate_labels[2], "score": .12},
                {"label": candidate_labels[3], "score": .07},
            ]

    monkeypatch.setattr(r, "_get_classifier", lambda: FakeModel())
    scores = r.classify_porsche_generation(Image.new("RGB", (16, 16)))
    assert abs(scores["997"] - .81) < 1e-10
    assert abs(scores["991"] - .19) < 1e-10


def test_997_compatível_mantem_sugestao_sem_confirmar_ano():
    slug, note = r.apply_porsche_generation_gate(
        r.PORSCHE_SLUG, "Sugestão CLIP.", {"997": .81, "991": .19}
    )
    assert slug == r.PORSCHE_SLUG
    assert "não confirma o ano" in note


def test_991_forte_rejeita_ficha_2010():
    slug, note = r.apply_porsche_generation_gate(
        r.PORSCHE_SLUG, "Sugestão CLIP.", {"997": .13, "991": .87}
    )
    assert slug is None
    assert "fora do catálogo" in note


def test_empate_nao_exibe_ficha_porsche_2010():
    slug, note = r.apply_porsche_generation_gate(
        r.PORSCHE_SLUG, "Sugestão CLIP.", {"997": .51, "991": .49}
    )
    assert slug is None
    assert "não foi possível" in note


def test_falha_verificacao_e_tratada_como_inconclusivo():
    slug, note = r.apply_porsche_generation_gate(r.PORSCHE_SLUG, "Sugestão", None)
    assert slug is None
    assert "não foi possível" in note


def test_outros_veiculos_mantem_classificacao_original():
    slug, note = r.apply_porsche_generation_gate(
        "fiat-uno", "Uno detectado", {"997": .02, "991": .98}
    )
    assert slug == "fiat-uno" and note == "Uno detectado"


def test_limite_heursitico_favorece_inconclusivo_se_proximo():
    assert r.decide_porsche_generation({"997": .61, "991": .39}) is None
    assert r.decide_porsche_generation({"997": .64, "991": .36}) == "997"
    assert r.decide_porsche_generation({"997": .34, "991": .66}) == "991"
