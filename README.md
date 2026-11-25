# AutoVision — Reconhecimento experimental de automóveis por imagens

Projeto acadêmico de **Computação Gráfica e Visão Computacional** desenvolvido em Python.

O AutoVision localiza automóveis em fotografias, sugere a correspondência com **cinco modelos de referência** e apresenta fichas técnicas históricas.

O sistema é um **protótipo experimental**: pode indicar resultados inconclusivos e não deve ser utilizado para identificar veículos de maneira pericial ou definitiva.

## 1. Objetivo e escopo

O projeto combina duas tarefas de visão computacional:

- **Detecção de objetos (YOLO11n):** localizar regiões compatíveis com a categoria genérica `car`.
- **Classificação visual por descrição (CLIP zero-shot):** comparar o recorte do automóvel com descrições dos cinco modelos cadastrados e categorias de contraste, inclusive modelos fora do catálogo.

Ao encontrar uma correspondência aceita pelas regras do protótipo, o programa consulta um catálogo **SQLite** e exibe uma ficha técnica de referência.

O AutoVision utiliza modelos pré-treinados. **Não foi treinado um novo modelo do zero** para os cinco automóveis.

### Modelos cadastrados

| Modelo | Recorte considerado no catálogo |
|---|---|
| Fiat Uno | Primeira geração, conhecido como “Uno quadrado” |
| Volkswagen Fusca | Modelo clássico Type 1, não New Beetle nem Beetle A5 |
| Chevrolet Opala SS | Família esportiva brasileira, diferentes carrocerias e motorizações |
| Porsche 911 GT3 RS | Referência técnica de 2010, geração 997.2 |
| Ford Mustang | Primeira série de 1964, usualmente chamada de 1964½ |

**Importante:** reconhecer semelhança visual com uma família ou modelo não confirma ano, motor, versão, originalidade ou geração exatos do veículo fotografado.

## 2. Tecnologias utilizadas

| Componente | Tecnologia | Função |
|---|---|---|
| Interface | Streamlit | Receber imagens e apresentar resultados |
| Detecção | Ultralytics YOLO11 nano (`yolo11n.pt`) | Localizar carros e desenhar caixas |
| Classificação | Hugging Face Transformers + CLIP (`openai/clip-vit-base-patch32`) | Comparação zero-shot com descrições textuais |
| Processamento | Pillow, NumPy e OpenCV | Preparação de imagens, recortes e estimativa de cor HSV |
| Catálogo | SQLite (`sqlite3`) | Armazenamento das fichas técnicas e fontes |
| Testes | pytest | Verificações automatizadas de funções e regras |

As dependências do Python estão especificadas em `requirements.txt`.

O projeto foi testado pela equipe em **Windows, Visual Studio Code e Python 3.13**, utilizando ambiente virtual `.venv` e execução em CPU.

## 3. Instalação e execução no Windows

Abra o terminal **PowerShell** na pasta raiz do projeto, onde está localizado o arquivo `app.py`.

É necessária conexão com a Internet para instalar as dependências e obter os pesos dos modelos YOLO e CLIP na primeira execução.

### Instalação completa

Execute os seguintes comandos:

```powershell
# Criar o ambiente virtual
py -3.13 -m venv .venv

# Instalar as dependências
.\.venv\Scripts\python.exe -m pip install -r requirements.txt

# Executar os testes automatizados
.\.venv\Scripts\python.exe -m pytest -q

# Iniciar a aplicação
.\.venv\Scripts\python.exe -m streamlit run app.py
```

Abra o endereço informado pelo Streamlit, normalmente:

http://localhost:8501

Para encerrar a aplicação, utilize `Ctrl+C` no terminal.

Se a porta estiver ocupada, o Streamlit poderá informar outro endereço local.

### Instalação reduzida para testes da interface

O projeto também disponibiliza o arquivo `requirements-interface.txt`, destinado a verificações da interface, do banco de dados e de funcionalidades que não exigem o carregamento dos modelos de inteligência artificial.

Para instalar somente essas dependências, depois de criar o ambiente virtual, execute:

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements-interface.txt
```

Essa instalação reduzida não inclui o YOLO nem o CLIP.

**Para executar o reconhecimento completo de automóveis, é necessário utilizar o arquivo `requirements.txt`.**

### Notas de execução

- O primeiro carregamento pode ser mais demorado devido ao download e carregamento dos pesos.
- A execução em CPU não exige placa de vídeo dedicada, mas o desempenho depende do computador.
- Os pesos dos modelos e o banco SQLite são recursos locais; não é necessário enviar os pesos ou o banco gerado ao GitHub.
- Não é obrigatório ativar o ambiente com `Activate.ps1` quando os comandos utilizam diretamente `.venv\Scripts\python.exe`.

## 4. Como utilizar

1. No menu **Analisar imagem**, envie uma fotografia JPG, PNG ou WEBP ou utilize a câmera.

2. Opcionalmente, delimite uma **região de interesse** com controles percentuais para excluir partes irrelevantes da cena.

3. Em **Passo 1 — Localizar os automóveis**, clique em **Detectar veículos na imagem**.

4. Caso várias caixas apareçam, escolha o veículo desejado na lista de detecções. A confiança exibida pelo YOLO refere-se somente à detecção genérica de um carro, não à marca ou ao modelo.

5. Em **Passo 2 — Identificar o modelo**, clique em **Analisar modelo selecionado**.

6. Consulte o modelo sugerido ou a mensagem de resultado inconclusivo, o recorte analisado, a visão geral e os tempos de processamento.

7. Se houver identificação, abra **Consultar ficha técnica completa e fontes**.

8. Opcionalmente, visualize as **pontuações CLIP e categorias de contraste** e faça uma amostragem da região pintada da carroceria para estimar sua cor aparente.

### Modo manual de contingência

Se o YOLO não localizar o automóvel, é possível ativar a opção **“Classificar a região selecionada SEM exigir detecção YOLO”**.

Nesse caso, o usuário confirma que a região escolhida contém o carro desejado, e o CLIP analisa diretamente o recorte.

**O resultado manual não comprova a presença de um automóvel nem representa sucesso da detecção automática.**

### Parâmetros ajustáveis

| Parâmetro | Valor de referência | Interpretação |
|---|---|---|
| Limiar YOLO | `0.30` | Limiar da detecção genérica de carro |
| Resolução YOLO | `640` | Tamanho de entrada; opções de `480` e `960` também estão disponíveis |
| Pontuação relativa mínima CLIP | `0.55` | Critério experimental para aceitar uma correspondência |
| Margem mínima entre 1º e 2º | `0.10` | Critério experimental para rejeitar resultados próximos |

Alterar esses valores pode modificar tanto os acertos quanto os erros.

**As pontuações do CLIP não são probabilidades calibradas de acerto.**

### Tratamento de falhas

A aplicação prevê mensagens e comportamentos específicos para situações como:

- Arquivo de imagem inválido ou incompatível.
- Problemas na captura de imagem pela câmera.
- Ausência de detecção de automóveis.
- Identificação inconclusiva.
- Necessidade de seleção manual de uma região de interesse.

Esses mecanismos ajudam a evitar que o sistema apresente identificações não confirmadas como resultados definitivos.

## 5. Arquitetura e fluxo de processamento

O processamento da aplicação segue as etapas:

```text
Fotografia (upload ou câmera)
            |
            v
Carregamento e pré-processamento
      (Pillow / OpenCV)
            |
            v
Região de interesse (opcional)
            |
            v
YOLO11n: detecção da categoria 'car'
            |
       +----+----+
       |         |
   Detectado   Não detectado
       |         |
Escolha da   Contingência
  caixa         manual
       |         |
       +----+----+
            |
            v
     Recorte do veículo
            |
            v
CLIP: comparação com descrições
 (cinco modelos + contrastes)
            |
            v
Regras de decisão e verificação
   de geração do Porsche
            |
       +----+----+
       |         |
Correspondência  Inconclusivo
       |         |
       v         v
 Consulta SQLite Aviso sem ficha
       |
       v
Ficha técnica de referência
       |
       v
Interface Streamlit
(recorte, métricas, pontuações,
cor aparente e fontes)
```

### Pré-processamento de imagens

O AutoVision utiliza diferentes operações de preparação e manipulação visual, incluindo:

- Redimensionamento de imagens.
- Recorte de regiões de interesse.
- Conversão e análise de cores.
- Preparação de imagens para os modelos pré-treinados.
- Conversão de coordenadas entre a imagem e os elementos de visualização.

Essas operações são utilizadas para adequar as entradas ao processamento e facilitar a interpretação dos resultados.

### Aspectos de Computação Gráfica

O aplicativo incorpora conceitos estudados na disciplina, entre eles:

- Mapeamento de coordenadas da imagem.
- Redimensionamento e preservação de proporções.
- Seleção e recorte de regiões de interesse.
- Desenho de caixas delimitadoras e rótulos.
- Composição de elementos gráficos sobre fotografias.
- Representação e análise visual de cores.
- Comparação entre imagem preparada, região analisada e resultado final.

A estimativa de cor é **experimental** e pode sofrer influência da iluminação, das sombras e dos reflexos.

### Organização do código

```text
AutoVision/
├── app.py
├── src/
│   ├── database.py
│   ├── preprocessing.py
│   ├── recognition.py
│   ├── vehicle_detection.py
│   └── visualization.py
├── tests/
├── docs/
│   ├── AutoVision_Apresentacao.pdf
│   └── AutoVision_Relatorio_Tecnico.pdf
├── screenshots/
│   └── README.md
├── data_samples/
│   ├── manifesto.csv
│   └── README.md
├── assets/
├── data/
├── requirements.txt
├── requirements-interface.txt
├── .gitignore
└── README.md
```

O banco SQLite local é criado em `data/autovision.sqlite3` durante a inicialização.

Alguns diretórios podem conter recursos adicionais ou arquivos produzidos durante o desenvolvimento.

## 6. Testes e resultados experimentais

A equipe realizou testes automatizados de código e avaliações experimentais com fotografias, incluindo diferentes ângulos, cores, condições visuais e veículos externos ao catálogo.

**Os resultados representam o conjunto de testes documentado, não uma taxa de acerto geral garantida.**

### Avaliação experimental

Foram registradas **36 avaliações**, distribuídas em quatro grupos:

| Grupo de avaliação | Resultado registrado | Interpretação |
|---|---|---|
| Identificação automática de modelos cadastrados | **14 acertos em 20 (70%)** | Seis resultados não foram conclusivos |
| Rejeição de veículos fora do catálogo | **6 rejeições em 7 (85,7%)** | Houve uma falsa aceitação |
| Controle negativo — imagens sem automóveis | **4 resultados adequados em 4** | Não houve atribuição indevida de um modelo |
| Contingência manual | **5 sugestões corretas em 5** | Resultados do CLIP sem confirmação de detecção YOLO |

### Resultados por modelo

Nos 20 testes automáticos com veículos cadastrados, foram observados:

| Modelo | Identificações corretas | Total |
|---|---:|---:|
| Fiat Uno | 2 | 4 |
| Volkswagen Fusca | 2 | 4 |
| Chevrolet Opala SS | 4 | 4 |
| Porsche 911 GT3 RS 2010 | 2 | 4 |
| Ford Mustang 1964½ | 4 | 4 |
| **Total** | **14** | **20** |

A amostra é pequena, portanto essas proporções não permitem uma estimativa robusta de desempenho em fotografias não avaliadas.

### Desempenho computacional

Nas 28 execuções com medições disponíveis, o tempo médio somado das etapas YOLO e CLIP foi de aproximadamente **0,45 segundo**.

Essa média não inclui necessariamente todos os componentes envolvidos no tempo total de resposta da interface.

Os tempos podem variar conforme o computador, o carregamento dos modelos, o tamanho da imagem e as condições da execução.

### Testes automatizados de software

A equipe executou a suíte de testes do projeto com pytest e confirmou **56 testes automatizados aprovados**.

Esses testes verificam funcionalidades e regras implementadas no código. Sua aprovação não deve ser confundida com a precisão estatística dos modelos de visão computacional.

Para executar novamente:

```powershell
.\.venv\Scripts\python.exe -m pytest -q
```

### Erros e dificuldades observados

Durante o desenvolvimento e a avaliação, foram identificadas situações como:

- Ausência de detecção de alguns automóveis em determinados enquadramentos.
- Resultados inconclusivos para imagens legítimas do catálogo.
- Aceitação incorreta de um veículo externo como Chevrolet Opala SS.
- Dificuldade de diferenciação entre modelos ou gerações semelhantes.
- Necessidade de seleção de automóveis em cenas com múltiplos veículos.
- Influência da iluminação na estimativa da cor da carroceria.

Essas situações foram consideradas na documentação técnica e na análise das limitações.

### Limitações e interpretação correta

- O YOLO identifica a categoria genérica `car`; sua confiança não representa identificação da marca ou do modelo.
- O CLIP compara imagens com descrições textuais previamente definidas.
- As pontuações do CLIP dependem das descrições concorrentes e não são probabilidades calibradas.
- As regras experimentais podem rejeitar imagens corretas ou aceitar veículos externos ao catálogo.
- A ficha técnica apresenta uma referência histórica, que pode não corresponder exatamente ao exemplar fotografado.
- O sistema não confirma ano, versão, motorização, placa, VIN, originalidade ou geração com certeza.

## 7. Reprodutibilidade e boas práticas

Para comparar resultados experimentais, recomenda-se registrar:

- Fotografia utilizada e sua procedência.
- Modelo esperado, quando aplicável.
- Parâmetros da análise.
- Modo automático ou manual.
- Resultado da detecção YOLO.
- Resultado da classificação CLIP.
- Tempo de processamento.
- Identificação de acertos, erros e respostas inconclusivas.

Para futuras avaliações, recomenda-se utilizar imagens independentes daquelas empregadas na definição de regras e limiares.

### Organização e segurança

Não devem ser versionados arquivos temporários ou recursos locais desnecessários, como:

- `.venv/`
- `__pycache__/`
- `.pytest_cache/`
- Pesos de modelos `*.pt`
- Bancos SQLite gerados localmente
- Senhas, tokens e credenciais
- Fotografias sem autorização de reutilização

Os caminhos utilizados pelo projeto devem ser mantidos de forma compatível com a estrutura documentada no repositório.

## 8. Fontes, licenças e créditos

### Bibliotecas e modelos

- **Ultralytics YOLO:** https://docs.ultralytics.com/
- **Modelo CLIP:** https://huggingface.co/openai/clip-vit-base-patch32
- **Hugging Face Transformers:** https://huggingface.co/docs/transformers/
- **Streamlit:** https://docs.streamlit.io/
- **OpenCV:** https://opencv.org/
- **PyTorch:** https://pytorch.org/
- **Pillow:** https://pillow.readthedocs.io/
- **pytest:** https://docs.pytest.org/

As fontes históricas utilizadas nas fichas dos veículos estão disponíveis nos links individuais do catálogo, na interface **Catálogo** e na consulta de ficha técnica.

### Fotografias de referência e demonstração

O repositório contém dez fotografias de exemplo obtidas do Wikimedia Commons, utilizadas como referências visuais e para demonstrações de funcionamento.

Essas imagens abrangem:

- Os cinco modelos de referência do catálogo.
- Veículos não cadastrados.
- Cenas contendo vários automóveis.
- Uma imagem de controle negativo, sem automóveis.

A autoria, a página original e a licença de cada fotografia estão registradas em:

`data_samples/manifesto.csv`

As condições de utilização e as finalidades das imagens estão documentadas em:

`data_samples/README.md`

As capturas de tela da aplicação estão acompanhadas de informações sobre as fotografias de terceiros presentes nelas:

`screenshots/README.md`

As fotografias permanecem sujeitas às licenças indicadas por seus respectivos autores.

### Declaração do uso de inteligência artificial

O desenvolvimento do AutoVision contou com modelos pré-treinados de inteligência artificial e com ferramentas de IA utilizadas como apoio às atividades acadêmicas.

**Modelos integrados à aplicação:**

- **YOLO11 nano (Ultralytics):** utilizado para localizar automóveis nas imagens.
- **CLIP (`openai/clip-vit-base-patch32`):** utilizado para comparar os recortes das imagens com descrições textuais dos veículos e categorias de contraste.

Ambos foram utilizados com pesos pré-treinados. Não foi realizado treinamento de um novo modelo do zero.

O CLIP realiza comparação entre representações visuais e textuais; não foi implementado um modelo generativo de linguagem para produzir respostas livres sobre as fotografias.

**Ferramentas de IA utilizadas como apoio ao desenvolvimento:**

- **ChatGPT (OpenAI):** utilizado como ferramenta auxiliar no planejamento do projeto, esclarecimento de conceitos, revisão de código, análise de resultados, organização dos testes e elaboração e revisão da documentação técnica.

- **Claude (Anthropic):** utilizado como ferramenta auxiliar na revisão e edição dos documentos acadêmicos, especialmente na substituição, organização e adequação das fotografias e capturas de tela do relatório técnico e dos slides de apresentação.

**Revisão e validação das contribuições das ferramentas:**

As sugestões e alterações realizadas com auxílio dessas ferramentas foram revisadas pela equipe, considerando a coerência com o funcionamento do aplicativo, a fidelidade aos resultados experimentais, a organização visual dos documentos e a procedência das fotografias utilizadas.

A validação do projeto incluiu:

- Execução e inspeção da interface.
- **56 testes automatizados de código aprovados.**
- **36 avaliações experimentais documentadas.**
- Conferência dos resultados apresentados no relatório técnico e nos slides.
- Registro das fontes e licenças das fotografias de demonstração.

Os integrantes são responsáveis pela compreensão, validação e apresentação das funcionalidades implementadas, das decisões técnicas, dos resultados e das limitações do sistema.

O uso das ferramentas de inteligência artificial como apoio não substitui a responsabilidade acadêmica dos autores.

### Considerações finais

O AutoVision foi desenvolvido para fins educacionais, como aplicação experimental de Computação Gráfica e Visão Computacional.

O projeto demonstra a integração de detecção de objetos, classificação visual por similaridade, processamento de imagens, representação gráfica, interação com o usuário e consulta a um catálogo técnico.

Os resultados obtidos evidenciam as possibilidades e limitações da solução, sem representar uma garantia de identificação exata de veículos em condições não avaliadas.

**Repositório:** https://github.com/PedroOliveiraH/AutoVision