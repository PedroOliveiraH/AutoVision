from src.recognition import CANDIDATES, decide


def test_cinco_classes():
    assert len(CANDIDATES) == 5


def test_rejeita_pontuacao_baixa():
    results = [
        {"slug": "fiat-uno", "score": 0.35},
        {"slug": "volkswagen-fusca", "score": 0.32},
    ]
    slug, _ = decide(results, 0.55, 0.10)
    assert slug is None


def test_aceita_pontuacao_alta():
    results = [
        {"slug": "fiat-uno", "score": 0.85},
        {"slug": "volkswagen-fusca", "score": 0.10},
    ]
    slug, _ = decide(results, 0.55, 0.10)
    assert slug == "fiat-uno"
