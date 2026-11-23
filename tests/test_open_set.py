from src.recognition import CANDIDATES, DISTRACTOR_LABELS, decide_with_alternatives


def test_conserva_cinco_modelos():
    assert len(CANDIDATES) == 5
    assert len(DISTRACTOR_LABELS) >= 5


def test_rejeita_contraste_externo():
    results = [{"slug": "fora-lamborghini", "score": 0.80},
               {"slug": "porsche-911-gt3-rs-2010", "score": 0.15}]
    slug, _ = decide_with_alternatives(results)
    assert slug is None


def test_aceita_candidato_do_catalogo_com_margem():
    results = [{"slug": "volkswagen-fusca", "score": 0.82},
               {"slug": "fora-outro", "score": 0.09}]
    slug, _ = decide_with_alternatives(results)
    assert slug == "volkswagen-fusca"


def test_rejeita_similaridade_ambigua():
    results = [{"slug": "fiat-uno", "score": 0.49},
               {"slug": "fora-gol", "score": 0.45}]
    slug, _ = decide_with_alternatives(results)
    assert slug is None
