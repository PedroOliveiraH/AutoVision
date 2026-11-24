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


# Exemplos adicionais para a comparação aberta: não constituem um catálogo
# exaustivo de veículos desconhecidos. NÃO garantem rejeição universal.
DISTRACTOR_LABELS = {
    "fora-lamborghini": "a Lamborghini Veneno angular Italian exotic supercar",
    "fora-gol": "a modern Volkswagen Gol compact Brazilian hatchback car",
    "fora-onix": "a modern Chevrolet Onix hatchback passenger car",
    "fora-corolla": "a Toyota Corolla modern sedan passenger car",
    "fora-suv": "a modern sports utility vehicle SUV car",
    "fora-picape": "a pickup truck with an open cargo bed",
    "fora-esportivo": "a modern angular supercar different from a Porsche 911",
    "fora-outro": "another brand or model of everyday passenger car",
    "fora-new-beetle": "a Volkswagen New Beetle from the 2000s with modern front engine and rounded body",
    "fora-beetle-a5": "a Volkswagen Beetle A5 from 2012 to 2019, redesigned modern compact coupe",
}

# A descrição de Porsche 991 adicionada na Etapa 3 foi retirada do ranking.
# Era visualmente muito semelhante à classe Porsche 997.2 do catálogo e
# provocou regressões nos exemplos de desenvolvimento. Isso NÃO significa
# que o CLIP consiga diferenciar automaticamente a geração 991 da 997.2.



def classify_with_alternatives(image):
    """Classifica com cinco modelos E candidatos de contraste adicionais.

    As pontuações mudam porque o conjunto de rótulos é diferente da Etapa 1.
    Não são probabilidades calibradas nem uma solução completa de open-set.
    """
    model = _get_classifier()
    descriptions = {**CANDIDATES, **DISTRACTOR_LABELS}
    labels = list(descriptions.values())
    scores = model(image, candidate_labels=labels,
                   hypothesis_template="This is a photo of {}.")
    reverse = {v: k for k, v in descriptions.items()}
    return [{"slug": reverse[s["label"]], "score": float(s["score"])} for s in scores]


def decide_with_alternatives(results, minimum_score=0.55, minimum_margin=0.10,
                             *, manual_mode=False):
    """Decide sem alegar detecção automática quando o modo é manual.

    A retirada do contraste Porsche 991 evita uma competição específica que
    apareceu na Etapa 3; isso não valida a geração/ano do Porsche sugerido.
    """
    if not results:
        return None, "Análise inconclusiva: nenhum resultado de classificação."
    first = results[0]
    if first["slug"] not in CANDIDATES:
        if manual_mode:
            return None, ("Nenhuma correspondência segura com os cinco modelos cadastrados. "
                          "No modo manual, não foi verificado se existe um automóvel na imagem.")
        return None, ("O YOLO detectou uma região compatível com automóvel, mas o CLIP "
                      "não encontrou correspondência segura com os cinco modelos cadastrados.")
    margin = first["score"] - (results[1]["score"] if len(results) > 1 else 0.0)
    if first["score"] < minimum_score or margin < minimum_margin:
        if manual_mode:
            return None, ("Classificação inconclusiva: pontuação ou margem insuficiente. "
                          "O modo manual não confirma a presença de automóvel.")
        return None, "Modelo inconclusivo: pontuação insuficiente ou categorias muito próximas."
    if manual_mode:
        return first["slug"], ("Sugestão visual do CLIP. A presença de automóvel não foi "
                               "confirmada pelo YOLO neste modo.")
    return first["slug"], "Sugestão de modelo — precisa de validação com fotos independentes."
