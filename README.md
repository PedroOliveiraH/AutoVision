# AutoVision — Reconhecimento experimental de cinco modelos de veículos

Projeto final acadêmico de Computação Gráfica. A equipe informou o valor da atividade como **50 pontos**.

## Estado atual — Etapa 4 (catálogo técnico)

Protótipo em Python + Streamlit com detecção genérica de carro via **YOLO11 nano**, classificação **CLIP zero-shot**, catálogo de cinco veículos no **SQLite** e interface de visualização. O desenvolvimento já teve testes exploratórios realizados no computador da equipe; **não há estimativa validada da acurácia geral**.

### Escopo do catálogo

1. Fiat Uno quadrado (primeira geração / família Mille da carroceria original)
2. Volkswagen Fusca clássico (Type 1; não New Beetle/A5)
3. Chevrolet Opala SS (motor e ano dependem da versão)
4. Porsche 911 GT3 RS 2010 (997.2; não qualquer 911 GT3 RS de outros anos)
5. Ford Mustang 1964½ (primeira série do ano/modelo 1965)

## Execução no Windows

A equipe está usando **Python 3.13.16**, VS Code e `.venv`, e já instalou as dependências essenciais. Para preparar uma instalação nova:

```powershell
py -3.13 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python -m pytest -q
python -m streamlit run app.py
```

A instalação precisa de Internet para baixar as dependências e, no primeiro reconhecimento, os pesos dos modelos YOLO e CLIP. A aplicação pode usar CPU e tende a demorar mais no primeiro carregamento.

## Como analisar uma fotografia

1. Em **Analisar imagem**, envie uma fotografia ou utilize a câmera.
2. Opcionalmente, ajuste a **região de interesse** por coordenadas percentuais para restringir o cenário.
3. Clique em **Detectar veículos na imagem**.
4. Se houver várias caixas, selecione o automóvel desejado na lista. As caixas aparecem numeradas na imagem.
5. Clique em **Analisar modelo selecionado**. A classificação trabalha com o recorte escolhido.
6. Se o YOLO falhar, marque a opção de **classificação manual sem YOLO**, confirme que o recorte contém o veículo e execute o CLIP. A detecção não foi confirmada nesse modo.
7. Opcionalmente, indique uma pequena **região pintada da carroceria** para a estimativa HSV de cor; evite pneus, vidros e fundo.

**Avisos:** os rótulos do CLIP são aproximações por similaridade entre descrições, não probabilidades de acerto. O sistema não identifica com garantia ano de fabricação, versão, placa ou VIN. Pode confundir carros de gerações parecidas, miniaturas e veículos não cadastrados. As fichas técnicas históricas foram preenchidas na Etapa 4, sem supor que a foto revele a configuração exata.

## Pipeline de visão e computação gráfica

- **Entrada:** imagens JPG, PNG, WEBP ou câmera; orientação EXIF e limite de tamanho.
- **Pré-processamento:** redimensionamento proporcional; suavização Gaussiana e conversão RGB→HSV na análise de cor; normalização própria do processador CLIP na classificação.
- **Detecção:** YOLO11 nano, classe COCO `car`, caixas e confiança de detecção separadas do modelo.
- **Seleção:** todas as detecções relevantes exibidas, seleção pelo usuário; alternativa manual declarada.
- **Classificação:** CLIP compara os cinco modelos do catálogo e contrastes como outros veículos, New Beetle e Beetle A5. A comparação específica com o Porsche 991 foi suspensa após uma regressão observada em testes; a geração exata não é garantida.
- **Representação gráfica:** coordenadas percentuais e absolutas, transformação ROI→imagem, caixas sobrepostas, rótulos, transparência e comparação visual.
- **Catálogo:** SQLite com cinco registros técnicos, migração de campos antigos, fontes consultadas e metadados de fotografias (sem usar placa ou identificação pessoal).
- **Avaliação:** testes unitários sem baixar pesos; testes reais e métricas a registrar com imagens independentes.

## Estrutura de arquivos

```text
app.py                     # Interface e controle de seleção
src/database.py            # Catálogo SQLite
src/preprocessing.py       # Entrada, recortes e cor HSV
src/recognition.py         # CLIP e contrastes
src/vehicle_detection.py   # YOLO e lista de caixas
src/visualization.py       # Caixas, legendas e camadas
requirements.txt           # Bibliotecas completas, incluindo ultralytics
tests/                    # Testes locais sem modelos de IA
data/                     # SQLite gerado localmente (não enviar ao Git)
data_samples/             # Manifesto de fotografias
INSTRUCOES_ETAPA3.md       # Guia seguro de instalação da atualização
docs/ETAPA3_PLANO_TESTE.md # Casos de teste e métricas
```

## Organização e entrega

O histórico do GitHub deve preservar commits e contribuições individuais. Registre fonte e licença das imagens e dados técnicos, limitações, resultados de falhas e uso de modelos de IA. Não envie `.venv`, pesos `*.pt`, banco SQLite local nem segredos.

Consulte `INSTRUCOES_ETAPA3.md` para aplicar a atualização na cópia já instalada e `docs/ETAPA3_PLANO_TESTE.md` para validar as novas funcionalidades.

## Etapa 4 — Banco de dados técnico

As fichas passaram a conter período, motorização, combustível, carroceria, potência, transmissão e tração. A atualização é feita na inicialização, preservando campos personalizados e fotos/índices existentes. Consulte `INSTRUCOES_ETAPA4.md` e `docs/FONTES_FICHAS_TECNICAS.md` para as fontes e as regras da migração. O CLIP não verifica ano nem motor de um exemplar.
