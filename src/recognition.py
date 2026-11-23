"""Experimento de classificação zero-shot com CLIP.

A pontuação do CLIP é *relativa às classes oferecidas*, NÃO uma probabilidade
calibrada. Rejeitar com limiares não garante rejeitar veículos desconhecidos.
"""
from functools import lru_cache

# Inglês costuma ser a escolha mais estável para o CLIP base.
CANDIDATES = {
    "fiat-uno": "a classic first generation Fiat Uno boxy hatchback car",
    "volkswagen-fusca": "a classic Volkswagen Beetle Type 1 vintage car",
    "chevrolet-opala-ss": "a vintage Brazilian Chevrolet Opala SS muscle car",
    "porsche-911-gt3-rs-2010": "a 2010 Porsche 911 GT3 RS 997.2 sports car with rear wing",
    "ford-mustang-1964-meio": "a 1964 and a half classic first generation Ford Mustang car",
}


@lru_cache(maxsize=1)
def _get_classifier():
    # Carregamento tardio: o catálogo funciona mesmo sem dependências de IA.
    from transformers import pipeline
    return pipeline(
        task="zero-shot-image-classification",
        model="openai/clip-vit-base-patch32",
        device=-1,  # CPU por padrão; evita problemas em PCs sem placa dedicada.
    )


def classify(image):
    model = _get_classifier()
    labels = list(CANDIDATES.values())
    scores = model(image, candidate_labels=labels,
                   hypothesis_template="This is a photo of {}.")
    reverse = {v: k for k, v in CANDIDATES.items()}
    return [{"slug": reverse[s["label"]], "score": float(s["score"])} for s in scores]


def decide(results, minimum_score=0.55, minimum_margin=0.10):
    if not results:
        return None, "Não houve resultado."
    first = results[0]
    margin = first["score"] - (results[1]["score"] if len(results) > 1 else 0.0)
    if first["score"] < minimum_score or margin < minimum_margin:
        return None, "Identificação inconclusiva (resultado abaixo dos limites escolhidos)."
    return first["slug"], "Correspondência sugerida pelo modelo (não verificada)."
