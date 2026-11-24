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
    # Contrastes para sedas esportivos modernos. O Lancer visto por tras foi
    # confundido com o Porsche 911 por compartilhar um aerofolio grande.
    # Sao rotulos NEGATIVOS, nao novos veiculos no catalogo SQLite.
    "fora-lancer-evo-x": "a Mitsubishi Lancer Evolution X four door Japanese performance sedan with a large rear wing",
    "fora-seda-esportivo": "a modern modified four door sports sedan with a large rear spoiler",
}

# A descrição de Porsche 991 adicionada na Etapa 3 foi retirada do ranking.
# Era visualmente muito semelhante à classe Porsche 997.2 do catálogo e
# provocou regressões nos exemplos de desenvolvimento. Isso NÃO significa
# que o CLIP consiga diferenciar automaticamente a geração 991 da 997.2.
# A adicao de contrastes de Lancer/seda esportivo tambem altera o ranking e
# precisa ser validada com imagens independentes de Porsche e Mitsubishi.



# Verificação SECUNDÁRIA somente para candidatos Porsche GT3 RS.
# Não adicionar a geração 991 aos contrastes gerais: isso fez o 997.2
# perder para a classe concorrente nos testes da Etapa 3.
PORSCHE_SLUG = "porsche-911-gt3-rs-2010"
PORSCHE_GENERATION_DESCRIPTIONS = {
    "997": (
        "a 2010 Porsche 911 GT3 RS 997.2 older generation racing coupe with round headlights and a rear wing",
        "an older Porsche 911 GT3 RS from the 997 generation with smooth rear fenders and a large fixed wing",
    ),
    "991": (
        "a 2015 Porsche 911 GT3 RS 991.1 newer generation sports coupe with large side air intakes behind the doors",
        "a newer Porsche 911 GT3 RS from the 991 generation with front fender vents and broad aerodynamic air scoops",
    ),
}


def classify_porsche_generation(image):
    """Comparação extra 997 × 991, SEM alterar o ranking geral do CLIP.

    Retorna proporções RELATIVAS entre quatro descrições, não uma
    probabilidade calibrada de a foto ser de determinada geração.
    """
    descriptions = {
        label: generation
        for generation, labels in PORSCHE_GENERATION_DESCRIPTIONS.items()
        for label in labels
    }
    predictions = _get_classifier()(
        image, candidate_labels=list(descriptions),
        hypothesis_template="This is a photo of {}.",
    )
    totals = {generation: 0.0 for generation in PORSCHE_GENERATION_DESCRIPTIONS}
    for pred in predictions:
        if pred["label"] in descriptions:
            totals[descriptions[pred["label"]]] += float(pred["score"])
    total = sum(totals.values())
    if total <= 0:
        return {generation: 0.0 for generation in totals}
    return {generation: value / total for generation, value in totals.items()}


def decide_porsche_generation(scores, minimum_difference=0.25):
    """Retorna '997', '991' ou None quando o segundo estágio é ambíguo.

    O limiar é heurístico e PRECISA ser avaliado com imagens separadas.
    A escolha '997' não comprova subgeração 997.2 nem o ano 2010.
    """
    if not scores:
        return None
    older = float(scores.get("997", 0))
    newer = float(scores.get("991", 0))
    if older <= 0 and newer <= 0:
        return None
    if older - newer >= minimum_difference:
        return "997"
    if newer - older >= minimum_difference:
        return "991"
    return None


def apply_porsche_generation_gate(slug, message, generation_scores):
    """Impede que o 991 receba a ficha histórica 997.2 de 2010.

    Somente afeta sugestões do Porsche; outros modelos não se alteram.
    """
    if slug != PORSCHE_SLUG:
        return slug, message
    generation = decide_porsche_generation(generation_scores)
    if generation == "997":
        return slug, (message + " Segunda análise sugere a geração 997; "
                      "não confirma o ano nem a subgeração 997.2.")
    if generation == "991":
        return None, ("Porsche 911 detectado visualmente, mas a comparação "
                      "adicional favoreceu a geração 991, fora do catálogo "
                      "de cinco modelos. A identificação de geração é experimental.")
    return None, ("A imagem lembra um Porsche 911, mas não foi possível "
                  "diferenciar com segurança as gerações 997 e 991. "
                  "A ficha técnica de 2010 não será atribuída.")


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
