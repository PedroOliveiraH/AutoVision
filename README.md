# AutoVision — Reconhecimento experimental de automóveis por imagens

Projeto acadêmico de **Computação Gráfica e Visão Computacional** desenvolvido em Python. O AutoVision localiza automóveis em fotografias, sugere a correspondência com **cinco modelos de referência** e apresenta fichas técnicas históricas. O sistema é um **protótipo experimental**: pode indicar resultados inconclusivos e não deve ser utilizado para identificar veículos de maneira pericial ou definitiva.

## 1. Objetivo e escopo

Combinar duas tarefas diferentes de visão computacional:

- **Detecção de objetos (YOLO11n):** localizar regiões compatíveis com a categoria genérica `car`.
- **Classificação visual por descrição (CLIP zero-shot):** comparar o recorte do automóvel com descrições dos cinco modelos cadastrados e categorias de contraste, inclusive modelos que estão fora do catálogo.

Ao encontrar uma correspondência aceita pelas regras do protótipo, o programa consulta um catálogo **SQLite** e exibe a ficha técnica de referência. O AutoVision utiliza modelos pré-treinados; **não foi treinado um novo modelo do zero** para os cinco automóveis.

### Modelos cadastrados

| Modelo | Recorte considerado no catálogo |
| --- | --- |
| Fiat Uno | Primeira geração, conhecido como “Uno quadrado” |
| Volkswagen Fusca | Modelo clássico Type 1, não New Beetle nem Beetle A5 |
| Chevrolet Opala SS | Família esportiva brasileira, diferentes carrocerias e motorizações |
| Porsche 911 GT3 RS | Referência técnica de 2010, geração 997.2 |
| Ford Mustang | Primeira série de 1964, usualmente chamada de 1964½ |

**Importante:** reconhecer semelhança visual com uma família/modelo não confirma ano, motor, versão, originalidade ou geração exatos do veículo fotografado.

## 2. Tecnologias utilizadas

| Componente | Tecnologia | Função |
| --- | --- | --- |
| Interface | Streamlit | Receber imagens e apresentar resultados |
| Detecção | Ultralytics YOLO11 nano (`yolo11n.pt`) | Localizar carros e desenhar caixas |
| Classificação | Hugging Face Transformers + CLIP (`openai/clip-vit-base-patch32`) | Comparação zero-shot com descrições textuais |
| Processamento | Pillow, NumPy e OpenCV | Preparação das imagens, recortes e estimativa de cor HSV |
| Catálogo | SQLite (`sqlite3`) | Fichas técnicas e fontes de referência |
| Testes | pytest | Verificações automatizadas de funções e regras |

As dependências do Python estão especificadas em `requirements.txt`. O projeto foi testado pela equipe em **Windows, VS Code e Python 3.13**, usando ambiente virtual `.venv` e execução em CPU.

## 3. Instalação e execução no Windows

Abra o terminal **PowerShell** na pasta raiz do projeto (onde está `app.py`). É necessária conexão com a Internet para instalar as dependências e obter os pesos de YOLO e CLIP no primeiro uso.

```powershell
# Criar o ambiente virtual (se ainda não existir)
py -3.13 -m venv .venv

# Instalar as dependências no ambiente correto
.\.venv\Scripts\python.exe -m pip install -r requirements.txt

# Executar os testes automatizados
.\.venv\Scripts\python.exe -m pytest -q

# Iniciar a interface
.\.venv\Scripts\python.exe -m streamlit run app.py
```

Abra o endereço local informado pelo Streamlit, normalmente **http://localhost:8501**. Para encerrar, use `Ctrl+C` no terminal. Se a porta estiver ocupada, o Streamlit poderá informar outra URL.

**Notas de execução:**

- O primeiro carregamento pode ser mais demorado devido ao download e carregamento dos pesos.
- O uso de CPU não requer placa de vídeo dedicada, mas o desempenho depende do computador.
- Os arquivos do modelo e o banco SQLite são recursos locais: não é necessário enviar pesos ou banco gerado ao GitHub.
- Não é necessário ativar o ambiente com `Activate.ps1` quando os comandos usam diretamente `.venv\Scripts\python.exe`.

## 4. Como utilizar

1. No menu **Analisar imagem**, envie uma fotografia JPG, PNG ou WEBP, ou utilize a câmera.
2. Opcionalmente, delimite uma **região de interesse** com controles percentuais para excluir partes irrelevantes da cena.
3. Em **Passo 1 — Localizar os automóveis**, clique em **Detectar veículos na imagem**.
4. Caso várias caixas apareçam, escolha o veículo desejado na lista de detecções. A confiança exibida pelo YOLO refere-se **somente à detecção de um carro**, não à marca ou ao modelo.
5. Em **Passo 2 — Identificar o modelo**, clique em **Analisar modelo selecionado**.
6. Consulte o modelo sugerido ou a mensagem de resultado inconclusivo, o recorte analisado, a visão geral e os tempos de processamento. Se houver identificação, abra **Consultar ficha técnica completa e fontes**.
7. Opcionalmente, visualize as **pontuações CLIP e categorias de contraste** e faça uma amostragem da região pintada da carroceria para estimar a cor aparente.

### Modo manual de contingência

Se o YOLO não localizar o automóvel, é possível ativar **“Classificar a região selecionada SEM exigir detecção YOLO”**. Nesse caso, o usuário confirma que a região escolhida contém o carro desejado, e o CLIP analisa diretamente o recorte. **O resultado manual não comprova a presença de um automóvel nem representa um sucesso da detecção automática.**

### Parâmetros ajustáveis

| Parâmetro | Valor de referência usado na interface | Interpretação |
| --- | --- | --- |
| Limiar YOLO | `0.30` | Limiar da detecção genérica de carro |
| Resolução YOLO | `640` | Tamanho de entrada; versões de interface incluem `480` e `960` |
| Pontuação relativa mínima CLIP | `0.55` | Critério experimental para aceitar uma correspondência |
| Margem mínima entre 1º e 2º | `0.10` | Critério experimental para rejeitar resultados próximos |

Alterar esses valores pode modificar tanto os acertos quanto os erros. **Pontuações CLIP não são probabilidades calibradas de acerto.**

## 5. Arquitetura e fluxo de processamento

```text
Fotografia (upload ou câmera)
            |
            v
Carregamento e pré-processamento (Pillow / OpenCV)
            |
            v
Região de interesse (opcional)
            |
            v
YOLO11n: detecção da categoria 'car'
            |
        +---+---------------------+
        |                         |
  Há detecção                Sem detecção
        |                         |
Escolha da caixa          Contingência manual
        |                   (se autorizada)
        +------------+------------+
                     |
                     v
             Recorte do veículo
                     |
                     v
       CLIP: similaridade com descrições
        (cinco modelos + contrastes)
                     |
                     v
   Regras de decisão e verificação do Porsche
                     |
             +-------+---------+
             |                 |
        Correspondência     Inconclusivo
             |                 |
             v                 v
       Consulta SQLite     Aviso sem ficha
             |
             v
    Modelo e ficha técnica de referência
             |
             v
     Interface Streamlit: recorte, métricas,
     pontuações, cor aparente e fontes
```

### Aspectos de computação gráfica

O aplicativo utiliza recortes, preservação de proporções, conversão de coordenadas percentuais para pixels, caixas delimitadoras, rótulos e sobreposições nas imagens. A estimativa de cor é **experimental**, baseada na imagem ou em uma amostra manual da pintura, e pode ser afetada por iluminação, sombras e reflexos.

### Organização do código

```text
AutoVision/
├── app.py                    # Interface Streamlit e fluxo principal
├── src/
│   ├── database.py           # Catálogo SQLite e fichas históricas
│   ├── preprocessing.py      # Entrada, recortes e estimativa de cor
│   ├── recognition.py        # CLIP, contrastes e regras de decisão
│   ├── vehicle_detection.py  # YOLO e caixas delimitadoras
│   └── visualization.py      # Desenhos, rótulos e sobreposições
├── tests/                    # Testes automatizados
├── docs/                     # Documentação e materiais acadêmicos
├── data_samples/             # Material de exemplo, quando autorizado
├── assets/                   # Recursos de interface
├── data/                     # Banco SQLite gerado localmente
├── requirements.txt          # Dependências da aplicação
├── .gitignore                # Arquivos locais que não devem ser versionados
└── README.md                 # Este documento
```

Alguns diretórios podem estar vazios ou conter arquivos adicionais do desenvolvimento. O banco local é criado em `data/autovision.sqlite3` durante a inicialização.

## 6. Testes e resultados experimentais

A equipe realizou testes automatizados e baterias de testes com fotografias, incluindo diferentes cores, ângulos e veículos que não pertencem ao catálogo. **Os resultados abaixo descrevem o conjunto de testes registrado, e não uma taxa de acerto geral garantida.**

| Grupo de avaliação | Resultado registrado | Interpretação |
| --- | --- | --- |
| Identificação automática de modelos cadastrados | **14 acertos em 20** (70%) | Nem todas as imagens tiveram identificação conclusiva |
| Rejeição de veículos fora do catálogo | **6 rejeições em 7** (85,7%) | Houve uma falsa aceitação observada |
| Contingência manual | **5 sugestões corretas em 5** | Resultados do CLIP sem confirmação de detecção YOLO |

Nos testes automáticos, o Opala SS e o Mustang tiveram **4 acertos em 4 imagens por modelo**; Uno, Fusca e Porsche tiveram **2 acertos em 4** cada. Essas proporções se referem exclusivamente às imagens examinadas; a amostra é pequena e não fornece uma estimativa robusta de generalização.

Exemplos de dificuldades observadas:

- O YOLO deixou de localizar alguns carros conforme o ângulo, enquadramento ou cenário.
- O CLIP retornou resultados inconclusivos para algumas imagens legítimas do catálogo.
- Um veículo clássico externo ao catálogo foi aceito incorretamente como Opala SS.
- Modelos e gerações semelhantes, como Porsche 911 GT3 RS 997 e 991, exigem cuidado adicional.
- Em cenas com mais de um carro, o usuário precisa selecionar a caixa correspondente ao veículo de interesse.

O projeto também registrou execuções dos testes unitários com **56 testes aprovados** em 24/11/2026, conforme a saída local apresentada pela equipe. Para conferir o estado da versão instalada, execute novamente `python -m pytest -q` no ambiente do projeto.

### Limitações e interpretação correta

- YOLO identifica a categoria genérica `car`; sua confiança **não** representa identificação do modelo.
- CLIP compara o recorte com textos pré-definidos; as pontuações dependem das descrições concorrentes e **não** são probabilidades calibradas.
- As regras experimentais podem rejeitar imagens corretas e aceitar veículos de fora do catálogo.
- A ficha técnica descreve uma **referência histórica**, não necessariamente o exemplar da fotografia.
- O sistema não confirma ano, versão, motorização, originalidade, placa, VIN nem geração com certeza.
- As métricas precisam ser interpretadas segundo o conjunto avaliado e os parâmetros usados; não podem ser extrapoladas para qualquer fotografia.

## 7. Reprodutibilidade e boas práticas

Para comparar resultados, registre a foto de teste, o modelo esperado, a origem/autorização da imagem, os parâmetros usados, o modo automático/manual, a detecção, a classificação e o tempo. Prefira **fotos independentes** (não usadas para definir regras ou escolher limiares) quando desejar medir desempenho.

Não versione `.venv/`, `__pycache__/`, `.pytest_cache/`, `*.pt`, bancos `*.sqlite3`, senhas, tokens, imagens sem autorização ou arquivos temporários. Consulte e respeite as licenças dos modelos, bibliotecas, fotografias e fontes históricas.

## 8. Fontes e créditos

- **Ultralytics YOLO:** https://docs.ultralytics.com/
- **Modelo CLIP usado:** https://huggingface.co/openai/clip-vit-base-patch32
- **Hugging Face Transformers:** https://huggingface.co/docs/transformers/
- **Streamlit:** https://docs.streamlit.io/
- **OpenCV:** https://opencv.org/
- **PyTorch:** https://pytorch.org/
- **Fontes históricas dos veículos:** disponíveis nos links individuais do catálogo, na interface **Catálogo** e na consulta de ficha técnica.

Projeto desenvolvido para fins educacionais. As fontes bibliográficas e licenças de fotografias usadas na apresentação devem ser creditadas individualmente. O uso de modelos de IA pré-treinados e de ferramentas de apoio ao desenvolvimento deve ser declarado conforme as orientações da disciplina.
