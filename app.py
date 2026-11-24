"""AutoVision — Etapa 3: seleção de carro, fallback manual e contrastes.

O YOLO detecta a categoria genérica 'car'. O CLIP sugere uma identidade a partir
somente das descrições oferecidas; os scores não são probabilidades calibradas.
"""
import hashlib
import time

import streamlit as st

from src.database import get_all_vehicles, get_vehicle, get_vehicle_sources, init_db
from src.preprocessing import crop_percent, estimate_color, load_image
from src.recognition import (
    CANDIDATES, DISTRACTOR_LABELS, PORSCHE_SLUG,
    apply_porsche_generation_gate, classify_porsche_generation,
    classify_with_alternatives, decide_with_alternatives,
)
from src.visualization import annotate, annotate_detections

st.set_page_config(page_title="AutoVision", page_icon="🚘", layout="wide")
init_db()
st.title("🚘 AutoVision")
st.caption("Projeto de Computação Gráfica — detecção e reconhecimento experimental de cinco modelos")

with st.sidebar:
    pagina = st.radio("Menu", ["Analisar imagem", "Catálogo", "Sobre o projeto"])
    st.divider()
    st.subheader("Parâmetros de análise")
    conf_yolo = st.slider("Limiar YOLO — detecção de carro", 0.10, 0.80, 0.30, 0.05)
    image_size = st.selectbox("Resolução usada pelo YOLO", [480, 640, 960], index=1,
                              help="960 pode ajudar com carros pequenos, mas exige mais processamento.")
    min_score = st.slider("Pontuação relativa mínima do CLIP", 0.20, 0.95, 0.55, 0.05)
    min_margin = st.slider("Margem mínima entre 1º e 2º", 0.00, 0.50, 0.10, 0.01)
    st.caption("As pontuações CLIP são relativas às descrições oferecidas, não probabilidades de acerto.")

if pagina == "Catálogo":
    st.header("Cinco veículos cadastrados")
    for car in get_all_vehicles():
        with st.expander(f"{car['marca']} {car['modelo']} — {car['versao']}"):
            st.write(f"**Tipo:** {car['tipo']}")
            st.write(f"**Período:** {car['periodo']}")
            st.write(f"**Motorização:** {car['motorizacao']}")
            st.write(f"**Combustível:** {car['combustivel']}")
            st.write(f"**Carroceria:** {car['carroceria']}")
            st.write(f"**Potência:** {car['potencia']}")
            st.write(f"**Transmissão:** {car['transmissao']}")
            st.write(f"**Tração:** {car['tracao']}")
            st.write(f"**Observações:** {car['observacoes']}")
            st.caption("Ficha histórica de referência; identificação visual não comprova ano, motor ou versão exatos.")
            for fonte in get_vehicle_sources(car['slug']):
                st.markdown(f"[Fonte: {fonte['titulo']}]({fonte['url']})")
    st.info("As fichas representam famílias ou versões de referência; fotos não comprovam a configuração individual.")

elif pagina == "Sobre o projeto":
    st.header("Objetivo e estado da Etapa 3")
    st.write("**YOLO11 nano** localiza automóveis; **CLIP** compara as descrições dos cinco "
             "modelos e categorias de contraste; **SQLite** fornece as fichas técnicas.")
    st.write("**Novidade:** várias caixas detectadas com seleção pelo usuário e classificação "
             "manual de uma região quando a detecção automática falhar.")
    st.write("**Não identifica ano exato, geração com garantia, placa ou VIN.** Uma miniatura "
             "pode parecer um automóvel real para os modelos.")
    st.write("Computação Gráfica: mapeamento de coordenadas, recortes, manutenção de proporções, "
             "retângulos e rótulos em camada, comparação visual e análise HSV.")
    st.warning("Limiar YOLO e CLIP são experimentais. A classificação manual ignora a verificação "
               "de presença de automóvel. A acurácia deve ser medida em imagens independentes.")

else:
    st.header("Reconhecer por fotografia")
    tipo = st.radio("Escolha a origem", ["Enviar imagem", "Tirar foto"], horizontal=True)
    upload = (st.file_uploader("Imagem JPG, PNG ou WEBP (máx. 12 MB)", type=["jpg", "jpeg", "png", "webp"])
              if tipo == "Enviar imagem" else st.camera_input("Tire uma foto"))
    if upload is None:
        st.info("Envie uma imagem ou tire uma foto. Os modelos baixam pesos somente na primeira execução.")
        st.stop()

    payload = upload.getvalue()
    try:
        img = load_image(payload)
    except (ValueError, OSError) as exc:
        st.error(f"Não foi possível abrir a imagem: {exc}")
        st.stop()

    with st.expander("Opcional: selecionar uma região de interesse na imagem"):
        st.caption("Os controles são coordenadas percentuais. Use-os para restringir a busca "
                   "ao carro pretendido e excluir outros veículos do cenário.")
        c1, c2 = st.columns(2)
        left = c1.slider("Esquerda (%)", 0, 95, 0)
        right = c2.slider("Direita (%)", 5, 100, 100)
        top = c1.slider("Topo (%)", 0, 95, 0)
        bottom = c2.slider("Base (%)", 5, 100, 100)
    try:
        roi, manual_rect = crop_percent(img, left, top, right, bottom)
    except ValueError as exc:
        st.error(str(exc))
        st.stop()

    c_a, c_b = st.columns(2)
    with c_a:
        st.image(img, caption="Imagem preparada", use_container_width=True)
    with c_b:
        st.image(annotate(img, manual_rect, "Região de interesse selecionada"),
                 caption="Região em que o YOLO fará a busca", use_container_width=True)

    # Toda mudança de imagem, recorte ou configuração YOLO invalida caixas antigas.
    signature = hashlib.sha256(
        payload + f"{manual_rect}|{conf_yolo:.2f}|{image_size}".encode("utf-8")
    ).hexdigest()
    if st.session_state.get("autovision_signature") != signature:
        st.session_state.autovision_signature = signature
        st.session_state.pop("autovision_detected", None)
        st.session_state.pop("autovision_result", None)

    st.markdown("### Passo 1 — Localizar os automóveis")
    if st.button("Detectar veículos na imagem", type="primary"):
        try:
            from src.vehicle_detection import detect_car_boxes
            started = time.perf_counter()
            with st.spinner("Localizando automóveis (YOLO)..."):
                detections = detect_car_boxes(roi, confidence=conf_yolo, image_size=image_size)
            st.session_state.autovision_detected = {
                "signature": signature,
                "boxes": detections,
                "time": time.perf_counter() - started,
            }
            st.session_state.pop("autovision_result", None)
        except Exception as exc:
            st.error("Falha ao executar o YOLO. Verifique a instalação do pacote ultralytics.")
            st.code(str(exc))
            st.stop()

    detection = st.session_state.get("autovision_detected")
    if not detection or detection.get("signature") != signature:
        st.info("Clique em 'Detectar veículos na imagem' para continuar.")
        st.stop()

    cars = detection["boxes"]
    selected = None
    if cars:
        st.success(f"YOLO encontrou {len(cars)} automóvel(is). Escolha qual analisar.")
        choices = list(range(len(cars)))
        selected = st.selectbox(
            "Automóvel selecionado",
            choices,
            format_func=lambda i: (
                f"Carro {i + 1} — detecção {cars[i]['confidence']:.1%}, "
                f"posição x={cars[i]['box'][0]}, y={cars[i]['box'][1]}"
            ),
            key=f"car_index_{signature[:16]}",
        )
        st.image(annotate_detections(img, cars, selected, offset=manual_rect[:2]),
                 caption="Verde: outras detecções. Amarelo: veículo selecionado.",
                 use_container_width=True)
        st.caption("As caixas e os números vêm do YOLO. Sua confiança mede apenas a detecção "
                   "da categoria carro, não o modelo específico.")
    else:
        st.warning("YOLO não encontrou automóveis nesta região. Isso não prova que a imagem não tenha carro.")
        st.caption("Experimente diminuir o limiar YOLO, aumentar a resolução para 960 "
                   "ou utilizar a classificação manual abaixo.")

    st.markdown("### Passo 2 — Identificar o modelo")
    use_manual = st.checkbox(
        "Classificar a região selecionada SEM exigir detecção YOLO (modo manual de contingência)",
        value=False,
        help="Útil quando o YOLO não detecta o carro. O usuário assume que o recorte contém o objeto de interesse.",
    )
    manual_ok = True
    if use_manual:
        st.warning("A classificação manual **não confirma que existe um automóvel**. "
                   "Ela compara o recorte diretamente com as descrições do CLIP.")
        manual_ok = st.checkbox("Confirmo que a região selecionada contém o carro que desejo analisar.")
        if manual_rect == (0, 0, *img.size):
            st.caption("Dica: se houver outros objetos, ajuste o recorte no início da página.")

    can_classify = (bool(cars) or use_manual) and manual_ok
    if st.button("Analisar modelo selecionado", disabled=not can_classify):
        if use_manual:
            vehicle_crop = roi
            selection_identity = "manual"
        else:
            vehicle_crop = roi.crop(cars[selected]["box"])
            selection_identity = f"yolo-{selected}"
        try:
            started = time.perf_counter()
            with st.spinner("Comparando imagem com o catálogo e as categorias de contraste..."):
                results = classify_with_alternatives(vehicle_crop)
                # Duas passagens independentes: a segunda só é executada
                # quando a classe principal se parece com o Porsche cadastrado.
                generation_scores = (
                    classify_porsche_generation(vehicle_crop)
                    if results and results[0]["slug"] == PORSCHE_SLUG else None
                )
            st.session_state.autovision_result = {
                "porsche_generation_scores": generation_scores,
                "signature": signature,
                "selection": selection_identity,
                "results": results,
                "classification_time": time.perf_counter() - started,
                "crop_box": ((0, 0, *roi.size) if use_manual else cars[selected]["box"]),
                "manual": use_manual,
            }
        except Exception as exc:
            st.error("Falha ao classificar o recorte pelo CLIP.")
            st.code(str(exc))
            st.stop()

    saved = st.session_state.get("autovision_result")
    requested_selection = "manual" if use_manual else (f"yolo-{selected}" if cars else None)
    if not saved or saved.get("signature") != signature or saved.get("selection") != requested_selection:
        st.info("Escolha o carro e clique em 'Analisar modelo selecionado'.")
        st.stop()

    st.markdown("### Resultado da análise")
    vehicle_crop = roi.crop(saved["crop_box"])
    results = saved["results"]
    slug, message = decide_with_alternatives(
        results, min_score, min_margin, manual_mode=bool(saved["manual"])
    )
    if slug == PORSCHE_SLUG:
        slug, message = apply_porsche_generation_gate(
            slug, message, saved.get("porsche_generation_scores")
        )
    total = detection["time"] + saved["classification_time"]
    st.write(f"**Tempo YOLO:** {detection['time']:.2f} s · "
             f"**Tempo CLIP:** {saved['classification_time']:.2f} s · "
             f"**Soma:** {total:.2f} s")
    if saved["manual"]:
        st.warning("**Modo manual:** o resultado não foi precedido por detecção positiva do YOLO.")
    else:
        st.caption(f"Veículo selecionado: nº {selected + 1} — "
                   f"confiança de detecção YOLO: {cars[selected]['confidence']:.1%}.")
    st.image(vehicle_crop, caption="Recorte efetivamente enviado ao CLIP", use_container_width=True)

    if slug:
        vehicle = get_vehicle(slug)
        if vehicle:
            name = f"{vehicle['marca']} {vehicle['modelo']} {vehicle['versao']}"
            st.success(f"Modelo sugerido: {name}")
            st.write(f"**Tipo:** {vehicle['tipo']}")
            st.write(f"**Período:** {vehicle['periodo']}")
            st.write(f"**Motor:** {vehicle['motorizacao']}")
            st.write(f"**Combustível:** {vehicle['combustivel']}")
            st.write(f"**Carroceria:** {vehicle['carroceria']}")
            st.write(f"**Potência:** {vehicle['potencia']}")
            st.write(f"**Transmissão:** {vehicle['transmissao']}")
            st.write(f"**Tração:** {vehicle['tracao']}")
            st.write(f"**Descrição:** {vehicle['observacoes']}")
            st.caption("Ficha histórica de referência; a fotografia não confirma ano, motorização ou versão.")
            with st.expander("Fontes da ficha técnica"):
                for fonte in get_vehicle_sources(vehicle['slug']):
                    st.markdown(f"[Fonte: {fonte['titulo']}]({fonte['url']})")
            st.info(message)
            if slug == "porsche-911-gt3-rs-2010":
                st.caption("O CLIP não verifica o ano 2010 nem distingue com garantia "
                           "a geração 997.2 de outras gerações do 911 GT3 RS. "
                           "A ficha técnica é referente ao modelo cadastrado.")
    else:
        st.warning(message)

    generation_scores = saved.get("porsche_generation_scores")
    if generation_scores is not None:
        with st.expander("Diagnóstico experimental: gerações Porsche 997 e 991"):
            st.write(f"Compatibilidade relativa com geração 997: "
                     f"{generation_scores['997']:.1%}")
            st.write(f"Compatibilidade relativa com geração 991: "
                     f"{generation_scores['991']:.1%}")
            st.caption("Os dois valores são relativos às descrições usadas, "
                       "não são probabilidades nem comprovam ano ou geração.")

    with st.expander("Opcional: melhorar a estimativa de cor com uma amostra da pintura"):
        st.caption("Escolha uma área pequena que contenha somente a pintura: porta, teto ou capô. "
                   "Evite vidros, pneus, sombras, adesivos e fundo.")
        color_manual = st.checkbox("Usar região específica da carroceria para estimar a cor")
        color_crop = vehicle_crop
        if color_manual:
            cc1, cc2 = st.columns(2)
            color_left = cc1.slider("Cor: esquerda (%)", 0, 95, 25)
            color_right = cc2.slider("Cor: direita (%)", 5, 100, 75)
            color_top = cc1.slider("Cor: topo (%)", 0, 95, 35)
            color_bottom = cc2.slider("Cor: base (%)", 5, 100, 65)
            try:
                color_crop, color_rect = crop_percent(vehicle_crop, color_left, color_top,
                                                      color_right, color_bottom)
                st.image(annotate(vehicle_crop, color_rect, "Área amostrada para cor"),
                         caption="Confirme que a caixa cobre apenas a pintura.", use_container_width=True)
            except ValueError as exc:
                st.error(str(exc))
                color_crop = None
    if color_crop is not None:
        st.write(f"**Cor aparente (estimativa experimental):** {estimate_color(color_crop)}")
        st.caption("A cor não é obtida por segmentação automática da carroceria; "
                   "mesmo uma amostra manual pode sofrer influência da iluminação.")

    st.caption("Pontuações relativas CLIP entre cinco modelos e descrições de contraste — "
               "NÃO representam probabilidade calibrada de acerto.")
    for item in results:
        if item["slug"] in CANDIDATES:
            car = get_vehicle(item["slug"])
            desc = f"{car['marca']} {car['modelo']} {car['versao']}" if car else item["slug"]
        else:
            desc = "Contraste (fora do catálogo): " + DISTRACTOR_LABELS[item["slug"]]
        st.write(f"{desc}: {item['score']:.1%}")
