"""Verificação *experimental* e independente da geração GT3 RS com CLIP.

O reconhecimento geral continua inalterado. Esta comparação separada é executada
SOMENTE quando o ranking principal coloca o Porsche 997.2 em primeiro lugar.
Pontuações somadas por grupo são relativas aos oito textos nesta comparação:
não são probabilidades de ano/modelo nem asseguram identificação do GT3 RS 3.8.
"""
from math import isfinite

from src.recognition import _get_classifier

PORSCHE_SLUG = "porsche-911-gt3-rs-2010"

# Mesmo número de descrições por geração, para não favorecer um grupo pela
# quantidade de rótulos. Não usar a cor do veículo como critério principal.
GENERATION_PROMPTS = {
    "997.2": (
        "a 2010 Porsche 911 GT3 RS 3.8 generation 997.2 coupe with a large rear wing",
        "a 2009 to 2011 Porsche 997.2 GT3 RS sports car with oval headlights and classic front bumper",
        "an older Porsche 911 997 GT3 RS race inspired coupe with round headlights and a rear spoiler",
        "a Porsche 997 second generation 911 GT3 RS 3.8 seen from the side or rear",
    ),
    "991": (
        "a 2015 Porsche 911 GT3 RS 4.0 generation 991 coupe with a large rear wing",
        "a 2015 to 2018 Porsche 991 GT3 RS sports car with vents above the front wheel arches",
        "a newer Porsche 911 991 GT3 RS race inspired coupe with side air intakes behind the doors",
        "a Porsche 991 generation 911 GT3 RS 4.0 seen from the side or rear",
    ),
}

# Limiar experimental para a verificação binária. Deve ser avaliado com
# fotografias independentes. 60% neste universo de prompts NAO significa 60%
# de probabilidade de estar correto.
MIN_GENERATION_SHARE = 0.60
MIN_GENERATION_MARGIN = 0.20


def classify_porsche_generation(image):
    """Retorna valores RELATIVOS agregados {'997.2': ..., '991': ...}.

    A API `pipeline` retorna scores por texto; somamos os quatro textos de cada
    geração e normalizamos. Qualquer saída incompleta é considerada falha.
    """
    prompts = {label: generation
               for generation, descriptions in GENERATION_PROMPTS.items()
               for label in descriptions}
    raw = _get_classifier()(
        image,
        candidate_labels=list(prompts),
        hypothesis_template="This is a photo of {}.",
    )
    if not isinstance(raw, list) or len(raw) != len(prompts):
        raise ValueError("Comparação geracional CLIP retornou rótulos incompletos.")
    seen = set()
    totals = {generation: 0.0 for generation in GENERATION_PROMPTS}
    for item in raw:
        label = item.get("label")
        score = float(item.get("score", -1))
        if label not in prompts or label in seen or not isfinite(score) or score < 0:
            raise ValueError("Comparação geracional CLIP retornou valores inválidos.")
        seen.add(label)
        totals[prompts[label]] += score
    total = sum(totals.values())
    if total <= 0:
        raise ValueError("A comparação geracional CLIP retornou pontuação nula.")
    return {generation: score / total for generation, score in totals.items()}


def decide_porsche_generation(scores, *, min_share=MIN_GENERATION_SHARE,
                              min_margin=MIN_GENERATION_MARGIN):
    """Decisão cautelosa: '997.2', '991' ou None para inconclusivo."""
    if not isinstance(scores, dict) or set(scores) != set(GENERATION_PROMPTS):
        return None, "Geração inconclusiva: comparação não disponível."
    try:
        values = {key: float(value) for key, value in scores.items()}
    except (TypeError, ValueError, OverflowError):
        return None, "Geração inconclusiva: pontuações inválidas."
    if not all(isfinite(v) and v >= 0 for v in values.values()):
        return None, "Geração inconclusiva: pontuações inválidas."
    total = sum(values.values())
    if total <= 0 or not isfinite(total):
        return None, "Geração inconclusiva: pontuações inválidas."
    ordered = sorted(((label, value / total) for label, value in values.items()),
                     key=lambda p: p[1], reverse=True)
    winner, share = ordered[0]
    margin = share - ordered[1][1]
    # Evita rejeitar valores exatamente no limite por arredondamento binário.
    epsilon = 1e-9
    if share + epsilon < min_share or margin + epsilon < min_margin:
        return None, "Geração inconclusiva: 997.2 e 991 visualmente próximas nesta análise."
    if winner == "991":
        return "991", "A imagem é mais compatível com a geração 991, fora do catálogo de 2010."
    return "997.2", ("A imagem é mais compatível com a geração 997.2; "
                     "o ano e a versão exatos continuam não verificados.")


def guard_porsche_catalog_result(slug, generation_scores):
    """Impede exibir ficha do Porsche 2010 sem verificação geracional favorável.

    Sem alteração das decisões para os demais quatro veículos.
    """
    if slug != PORSCHE_SLUG:
        return slug, None
    generation, message = decide_porsche_generation(generation_scores)
    if generation == "997.2":
        return slug, message
    return None, message
