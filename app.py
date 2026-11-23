"""AutoVision: protótipo inicial de interface e classificação por fotografia."""
import time

import streamlit as st

from src.database import init_db, get_all_vehicles, get_vehicle
from src.preprocessing import load_image, crop_percent, estimate_color
from src.recognition import classify, decide
from src.visualization import annotate

st.set_page_config(page_title="AutoVision", page_icon="🚘", layout="wide")
init_db()

st.title("🚘 AutoVision")
st.caption("Protótipo acadêmico — identificação visual experimental de cinco modelos")

with st.sidebar:
    pagina = st.radio("Menu", ["Analisar imagem", "Catálogo", "Sobre o projeto"])
    st.divider()
    st.subheader("Parâmetros de análise")
    min_score = st.slider("Pontuação relativa mínima", 0.20, 0.95, 0.55, 0.05)
    min_margin = st.slider("Diferença mínima entre 1º e 2º", 0.00, 0.50, 0.10, 0.01)
    st.caption("Esses limites são experimentais; não representam confiança estatística calibrada.")

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
    st.header("Objetivo e estado do protótipo")
    st.write("Aplicação acadêmica que compara fotografias a cinco descrições de modelos usando CLIP e consulta um catálogo SQLite.")
    st.write("**Esta versão não faz detecção automática com YOLO, não confirma ano exato nem reconhece placa ou VIN.**")
    st.write("A área analisada pode ser selecionada manualmente por coordenadas percentuais.")
    st.write("**Operações implementadas:** redimensionamento proporcional; suavização Gaussiana e conversão RGB→HSV para análise exploratória de cor; normalização interna do processador CLIP.")
    st.write("**Computação Gráfica:** coordenadas percentuais→pixels, manutenção de proporção, caixas sobrepostas, transparência e comparação visual.")
    st.warning("O classificador só foi preparado no código. Precisamos medir sua precisão com fotografias independentes; limiares não garantem que modelos desconhecidos sejam rejeitados.")

else:
    st.header("Reconhecer por fotografia")
    tipo = st.radio("Escolha a origem", ["Enviar imagem", "Tirar foto"], horizontal=True)
    upload = (st.file_uploader("Imagem JPG, PNG ou WEBP (máx. 12 MB)", type=["jpg", "jpeg", "png", "webp"])
              if tipo == "Enviar imagem" else st.camera_input("Tire uma foto de um veículo"))
    if upload is None:
        st.info("Selecione ou capture uma foto para iniciar. Na primeira análise com IA, o modelo precisa ser baixado da internet.")
    else:
        try:
            img = load_image(upload.getvalue())
        except (ValueError, OSError, Exception) as exc:
            st.error(f"Não foi possível abrir a imagem: {exc}")
            st.stop()

        with st.expander("Opcional: selecionar manualmente uma região da imagem"):
            st.caption("Escolha uma área onde o carro aparece. Os valores são porcentagens da imagem.")
            c1, c2 = st.columns(2)
            left = c1.slider("Esquerda (%)", 0, 95, 0)
            right = c2.slider("Direita (%)", 5, 100, 100)
            top = c1.slider("Topo (%)", 0, 95, 0)
            bottom = c2.slider("Base (%)", 5, 100, 100)
        try:
            crop, rect = crop_percent(img, left, top, right, bottom)
        except ValueError as exc:
            st.error(str(exc))
            st.stop()

        c_a, c_b = st.columns(2)
        with c_a:
            st.image(img, caption="Imagem preparada", use_container_width=True)
        with c_b:
            st.image(annotate(img, rect, "Regiao selecionada manualmente"),
                     caption="Região analisada (caixa manual, não detecção YOLO)", use_container_width=True)
        if st.button("Analisar veículo", type="primary"):
            started = time.perf_counter()
            try:
                with st.spinner("Executando classificação visual experimental..."):
                    results = classify(crop)
                elapsed = time.perf_counter() - started
            except Exception as exc:
                st.error("Não foi possível executar o modelo visual. Confirme a instalação das dependências e a conexão para baixar o CLIP.")
                st.code(str(exc))
                st.stop()

            slug, message = decide(results, min_score, min_margin)
            st.subheader("Resultado da análise")
            st.write(f"**Tempo da análise:** {elapsed:.2f} s (inclui carregamento inicial, quando aplicável)")
            if slug:
                vehicle = get_vehicle(slug)
                name = f"{vehicle['marca']} {vehicle['modelo']} {vehicle['versao']}"
                st.success(f"Modelo sugerido: {name}")
                st.image(annotate(img, rect, "Modelo sugerido: " + name), use_container_width=True)
                st.write(f"**Tipo:** {vehicle['tipo']}")
                st.write(f"**Período:** {vehicle['periodo']}")
                st.write(f"**Motor:** {vehicle['motorizacao']}")
                st.write(f"**Combustível:** {vehicle['combustivel']}")
                st.write(f"**Descrição:** {vehicle['observacoes']}")
                st.info(message)
            else:
                st.warning(message)
            st.write(f"**Cor aparente (estimativa experimental):** {estimate_color(crop)}")
            st.caption("A estimativa pode refletir fundo, sombras ou vidros. Não representa segmentação da carroceria.")
            st.caption("Pontuações relativas do CLIP entre as cinco classes: NÃO equivalem a probabilidade de acerto.")
            for item in results:
                candidate = get_vehicle(item['slug'])
                st.write(f"{candidate['marca']} {candidate['modelo']} {candidate['versao']}: {item['score']:.1%}")
