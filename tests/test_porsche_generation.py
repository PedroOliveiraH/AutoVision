"""Refinamento Porsche: testes de integração lógica, NÃO medem acerto fotográfico."""
import math

import pytest
from PIL import Image

from src.porsche_generation import (
    PORSCHE_SLUG, GENERATION_PROMPTS,
    classify_porsche_generation, decide_porsche_generation,
    guard_porsche_catalog_result,
)
from src.recognition import CANDIDATES, DISTRACTOR_LABELS, decide_with_alternatives


def test_as_cinco_classes_originais_nao_mudam():
    assert len(CANDIDATES) == 5
    assert PORSCHE_SLUG in CANDIDATES
    assert 'fora-porsche-991' not in DISTRACTOR_LABELS
    assert set(GENERATION_PROMPTS) == {'997.2', '991'}
    assert len(GENERATION_PROMPTS['997.2']) == len(GENERATION_PROMPTS['991']) == 4


def test_classificador_geracional_usa_o_mesmo_modelo_e_oito_descricoes(monkeypatch):
    class ClassificadorSimulado:
        def __call__(self, image, candidate_labels, hypothesis_template):
            assert image.size == (20, 16)
            assert len(candidate_labels) == 8
            assert hypothesis_template == 'This is a photo of {}.'
            assert any('997.2' in label for label in candidate_labels)
            assert any('991' in label for label in candidate_labels)
            assert not any('Fiat Uno' in label for label in candidate_labels)
            return [{'label': label, 'score': .20 if i < 4 else .05}
                    for i, label in enumerate(candidate_labels)]

    monkeypatch.setattr('src.porsche_generation._get_classifier', lambda: ClassificadorSimulado())
    result = classify_porsche_generation(Image.new('RGB', (20, 16)))
    assert result['997.2'] == pytest.approx(.8)
    assert result['991'] == pytest.approx(.2)
    assert sum(result.values()) == pytest.approx(1.0)


def test_erro_se_o_clip_retornar_resultados_incompletos(monkeypatch):
    class ClasseIncompleta:
        def __call__(self, image, candidate_labels, hypothesis_template):
            return [{'label': candidate_labels[0], 'score': 1.0}]
    monkeypatch.setattr('src.porsche_generation._get_classifier', lambda: ClasseIncompleta())
    with pytest.raises(ValueError, match='incompletos'):
        classify_porsche_generation(Image.new('RGB', (8, 8)))


def test_erro_se_o_clip_retornar_rotulo_repetido(monkeypatch):
    class ClasseRepetida:
        def __call__(self, image, candidate_labels, hypothesis_template):
            return [{'label': candidate_labels[0], 'score': .125} for _ in candidate_labels]
    monkeypatch.setattr('src.porsche_generation._get_classifier', lambda: ClasseRepetida())
    with pytest.raises(ValueError, match='inválidos'):
        classify_porsche_generation(Image.new('RGB', (8, 8)))


def test_997_compatibilidade_suficiente():
    label, msg = decide_porsche_generation({'997.2': .77, '991': .23})
    assert label == '997.2'
    assert 'não verificados' in msg


def test_991_suficiente_rejeita_ficha_de_2010():
    label, msg = decide_porsche_generation({'997.2': .18, '991': .82})
    assert label == '991'
    assert 'fora do catálogo' in msg


def test_proximo_do_limiar_e_conservador():
    assert decide_porsche_generation({'997.2': .59, '991': .41})[0] is None
    assert decide_porsche_generation({'997.2': .60, '991': .40})[0] == '997.2'
    assert decide_porsche_generation({'997.2': .51, '991': .49})[0] is None


def test_saida_invalida_ou_ausente_nao_libera_a_ficha():
    for value in (None, {}, {'997.2': .7}, {'997.2': float('nan'), '991': .2},
                  {'997.2': 0, '991': 0}, {'997.2': -1, '991': 2}):
        assert decide_porsche_generation(value)[0] is None
        assert guard_porsche_catalog_result(PORSCHE_SLUG, value)[0] is None


def test_guarda_ficha_porsche_so_quando_997_compativel():
    assert guard_porsche_catalog_result(PORSCHE_SLUG, {'997.2': .85, '991': .15})[0] == PORSCHE_SLUG
    assert guard_porsche_catalog_result(PORSCHE_SLUG, {'997.2': .10, '991': .90})[0] is None
    assert guard_porsche_catalog_result(PORSCHE_SLUG, {'997.2': .52, '991': .48})[0] is None


def test_guarda_nao_altera_outros_quatro_modelos():
    for slug in CANDIDATES:
        if slug != PORSCHE_SLUG:
            assert guard_porsche_catalog_result(slug, None) == (slug, None)


def test_fluxo_geral_ainda_aceita_porsche_e_segunda_passagem_pode_rejeitar():
    original = [
        {'slug': PORSCHE_SLUG, 'score': .88},
        {'slug': 'fora-lancer-evo-x', 'score': .08},
        {'slug': 'fiat-uno', 'score': .04},
    ]
    slug, _ = decide_with_alternatives(original)
    assert slug == PORSCHE_SLUG
    assert guard_porsche_catalog_result(slug, {'997.2': .20, '991': .80})[0] is None


def test_lancer_e_rejeitado_sem_acionar_guarda_porsche():
    original = [
        {'slug': 'fora-lancer-evo-x', 'score': .78},
        {'slug': PORSCHE_SLUG, 'score': .15},
    ]
    slug, _ = decide_with_alternatives(original, manual_mode=True)
    assert slug is None
    assert guard_porsche_catalog_result(slug, None)[0] is None


def test_app_guarda_resultado_antes_de_exibir_ficha_e_separa_tempos():
    """Inspeção da integração: execução fotográfica cabe à validação no Windows."""
    from pathlib import Path
    app = (Path(__file__).resolve().parents[1] / 'app.py').read_text(encoding='utf-8')
    assert "classify_porsche_generation(vehicle_crop)" in app
    assert 'results[0]["slug"] == PORSCHE_SLUG' in app
    assert '"porsche_generation_scores": generation_scores' in app
    assert 'saved.get("porsche_generation_scores")' in app
    assert 'slug, message = apply_porsche_generation_gate(' in app
    assert app.index('slug, message = apply_porsche_generation_gate(') < app.index('vehicle = get_vehicle(slug)')
    assert '"classification_time":' in app
    assert 'detection["time"] + saved["classification_time"]' in app