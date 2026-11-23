"""AutoVision: protótipo com detecção de presença + comparação de modelos.

A etapa 2 usa YOLO nano para localizar automóveis, e só então usa CLIP para
sugerir um dos cinco modelos ou uma resposta inconclusiva. Sem garantia de
reconhecer todos os casos de fora do catálogo.
"""
import time

import streamlit as st

from src.database import init_db, get_all_vehicles, get_vehicle
from src.preprocessing import load_image, crop_percent, estimate_color
from src.recognition import classify_with_alternatives, decide_with_alternatives, CANDIDATES, DISTRACTOR_LABELS
from src.visualization import annotate

st.set_page_config(page_title="AutoVision", page_icon="🚘", layout="wide")
init_db()

st.title("🚘 AutoVision")
st.caption("Protótipo acadêmico — detecção de veículos e identificação visual experimental")

with st.sidebar:
    pagina = st.radio("Menu", ["Analisar imagem", "Catálogo", "Sobre o projeto"])
    st.divider()
    st.subheader("Parâmetros de análise")
    conf_yolo = st.slider("Limiar de detecção de carro (YOLO)", 0.10, 0.80, 0.30, 0.05)
    min_score = st.slider("Pontuação CLIP mínima entre todas as descrições", 0.20, 0.95, 0.55, 0.05)
    min_margin = st.slider("Diferença mínima entre 1º e 2º", 0.00, 0.50, 0.10, 0.01)
    st.caption("Os limites são heurísticos: não correspondem à probabilidade calibrada de acerto.")

if pagina == "Catálogo":
    st.header("Cinco veículos cadastrados")
    for car in get_all_vehicles():
        with st.expander(f"{car['marca']} {car['modelo']} — {car['versao']}"):
            st.write(f"**Tipo:** {car['tipo']}")
            st.write(f"**Período:** {car['periodo']}")
            st.write(f"**Motorização:** {car['motorizacao']}")
            st.write(f"**Combustível:** {car['combustivel']}")
            st.write(car['observacoes'])
            if car['fonte_url']:
                st.markdown(f"[Fonte técnica / referência inicial]({car['fonte_url']})")
    st.info("Dados 'A definir' dependem da pesquisa do recorte exato de cada carro.")

elif pagina == "Sobre o projeto":
    st.header("Objetivo e estado da Etapa 2")
    st.write("A aplicação usa **YOLO11 nano** para localizar um carro na fotografia, **CLIP** para comparar o recorte com as cinco categorias e descrições de contraste e um **catálogo SQLite** para a ficha técnica.")
    st.write("**Não confirma ano de fabricação, versão exata, placa ou VIN.** Não substitui avaliação visual humana.")
    st.write("Pré-processamento: redimensionamento proporcional; suavização Gaussiana; conversão RGB→HSV; normalização interna do CLIP.")
    st.write("Computação Gráfica: coordenadas percentuais→pixels, caixa de detecção YOLO, manutenção de proporção, camadas e sobreposição de caixas, comparação visual.")
    st.warning("A detecção YOLO pode errar, e as descrições adicionais do CLIP não resolvem completamente o problema de veículos desconhecidos. É obrigatório avaliar os erros em imagens independentes.")

else:
    st.header("Reconhecer por fotografia")
    tipo = st.radio("Escolha a origem", ["Enviar imagem", "Tirar foto"], horizontal=True)
    upload = (st.file_uploader("Imagem JPG, PNG ou WEBP (máx. 12 MB)", type=["jpg", "jpeg", "png", "webp"])
              if tipo == "Enviar imagem" else st.camera_input("Tire uma foto de um veículo"))
    if upload is None:
        st.info("Envie uma imagem ou tire uma foto. O YOLO e o CLIP precisam baixar os pesos na primeira execução.")
    else:
        try:
            img = load_image(upload.getvalue())
        except (ValueError, OSError) as exc:
            st.error(f"Não foi possível abrir a imagem: {exc}")
            st.stop()

        with st.expander("Opcional: selecionar manualmente uma região da imagem"):
            st.caption("Recorte para facilitar a localização de um carro específico. Não substitui a verificação YOLO.")
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
            st.image(annotate(img, manual_rect, "Região de interesse manual"),
                     caption="Região selecionada para verificar com YOLO", use_container_width=True)

        if st.button("Analisar veículo", type="primary"):
            started = time.perf_counter()
            try:
                from src.vehicle_detection import best_car_box
                with st.spinner("Verificando a presença de automóvel (YOLO)..."):
                    box, conf = best_car_box(roi, confidence=conf_yolo)
            except Exception as exc:
                st.error("Falha ao carregar ou executar a detecção YOLO. Confirme `pip install ultralytics` e a conexão inicial à internet.")
                st.code(str(exc))
                st.stop()

            st.subheader("Resultado da análise")
            if box is None:
                st.warning("Nenhum automóvel detectado. Não tentamos classificar a imagem pelo CLIP.")
                st.write(f"**Tempo total:** {time.perf_counter() - started:.2f} s")
                st.caption("O YOLO pode deixar de detectar um carro por oclusão, iluminação ou ângulo.")
                st.stop()

            x1, y1, x2, y2 = box
            # ROI está relativa ao recorte; converte de volta às coordenadas da imagem original.
            offset_x, offset_y = manual_rect[:2]
            rect_original = (x1 + offset_x, y1 + offset_y, x2 + offset_x, y2 + offset_y)
            vehicle_crop = roi.crop(box)
            st.image(annotate(img, rect_original, "Carro detectado (YOLO)"),
                     caption=f"Caixa automática — YOLO, confiança de detecção: {conf:.1%}", use_container_width=True)
            try:
                with st.spinner("Comparando o modelo com o catálogo e descrições de contraste..."):
                    results = classify_with_alternatives(vehicle_crop)
            except Exception as exc:
                st.error("Erro na classificação CLIP.")
                st.code(str(exc))
                st.stop()

            elapsed = time.perf_counter() - started
            slug, message = decide_with_alternatives(results, min_score, min_margin)
            st.write(f"**Tempo total de análise:** {elapsed:.2f} s")
            if slug:
                vehicle = get_vehicle(slug)
                if vehicle:
                    name = f"{vehicle['marca']} {vehicle['modelo']} {vehicle['versao']}"
                    st.success(f"Modelo sugerido: {name}")
                    st.write(f"**Tipo:** {vehicle['tipo']}")
                    st.write(f"**Período:** {vehicle['periodo']}")
                    st.write(f"**Motor:** {vehicle['motorizacao']}")
                    st.write(f"**Combustível:** {vehicle['combustivel']}")
                    st.write(f"**Descrição:** {vehicle['observacoes']}")
                    st.info(message)
            else:
                st.warning(message)
            st.write(f"**Cor aparente (estimativa experimental):** {estimate_color(vehicle_crop)}")
            st.caption("A cor é estimada na caixa detectada, mas fundo, vidros e faixas ainda podem interferir.")
            st.caption("Pontuações relativas CLIP entre cinco modelos + descrições de contraste: NÃO são probabilidades de acerto.")
            for item in results:
                if item["slug"] in CANDIDATES:
                    car = get_vehicle(item["slug"])
                    desc = f"{car['marca']} {car['modelo']} {car['versao']}" if car else item['slug']
                else:
                    desc = "Contraste (fora do catálogo): " + DISTRACTOR_LABELS[item["slug"]]
                st.write(f"{desc}: {item['score']:.1%}")
