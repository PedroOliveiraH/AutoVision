# AutoVision — reconhecimento visual experimental de cinco veículos

Projeto final acadêmico de Computação Gráfica (50 pontos, informado pela equipe).

## Estado atual

Este é um **protótipo inicial, ainda não validado com fotografias**.
A interface, o banco SQLite e a classificação zero-shot com CLIP estão implementados,
mas a acurácia real ainda precisa ser testada. Não há detecção automática YOLO,
nem confirmação do ano exato ou da motorização por fotografia.

## Os cinco veículos

1. Fiat Uno quadrado (primeira geração)
2. Volkswagen Fusca clássico
3. Chevrolet Opala SS (ano/carroceria ainda a definir)
4. Porsche 911 GT3 RS 2010 (997.2)
5. Ford Mustang 1964½ (ano/modelo 1965)

## Requisitos

- Python **3.11** recomendado
- Computador com internet no primeiro uso de IA, para baixar o modelo CLIP
- Aproximadamente 1 GB ou mais de espaço disponível para dependências e pesos (varia por plataforma)
- Git para registrar contribuições

## Instalação no Windows (PowerShell)

Abra o PowerShell na pasta que contém `app.py`:

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python -m streamlit run app.py
```

Caso o comando `py -3.11` não esteja disponível, confira `py --list` e a instalação do Python 3.11.
Se o PowerShell impedir a ativação, rode os executáveis diretamente:

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m streamlit run app.py
```

### Apenas testar interface e banco, sem baixar bibliotecas pesadas de IA

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements-interface.txt
.\.venv\Scripts\python.exe -m streamlit run app.py
```

Nesse modo, as páginas do catálogo funcionam, mas ao clicar em **Analisar veículo** a classificação informará que falta instalar o pacote completo.

## Testes unitários

```powershell
python -m pytest -q
```

Eles testam banco, pré-processamento, regras básicas e a estrutura, **não** demonstram acurácia da IA.

## Como usar

1. Na aba `Catálogo`, veja os cinco registros.
2. Em `Analisar imagem`, envie JPG/PNG/WEBP ou tire uma foto.
3. Se desejar, recorte uma região manual por porcentagens (não é detecção automática).
4. Ajuste na lateral a pontuação mínima e a diferença entre as primeiras classes.
5. Clique em `Analisar veículo` para carregar o CLIP e produzir uma sugestão.
6. Confira a pontuação relativa, ficha do SQLite e estimativa exploratória de cor.

**Atenção:** o classificador CLIP compara apenas cinco descrições e pode identificar
erroneamente carros de outras classes; os limiares são heurísticos e não
probabilidades de acerto. A cor estimada pode refletir o fundo e outros objetos.

## Pipeline e conceitos gráficos

- Aquisição: arquivo enviado ou câmera pelo navegador.
- Preparação: leitura validada, orientação EXIF, conversão RGB e redimensionamento proporcional com OpenCV.
- Pré-processamento: suavização Gaussiana e espaço HSV para cor; processador CLIP aplica suas normalizações internas para classificação.
- Visão: CLIP zero-shot entre cinco descrições, sem treinamento local.
- Representação gráfica: região de interesse selecionada manualmente, conversão de coordenadas percentuais para pixels, retângulo, camada semitransparente, rótulo e imagens lado a lado.
- Interação: origem da imagem, região de interesse, limite de pontuação e margem entre classes.
- Avaliação: testes unitários incluídos; medir desempenho real conforme docs/PLANO_TESTES.md.

## Estrutura de pastas

```text
app.py                  # Interface Streamlit
src/database.py         # SQLite com 5 registros e tabela de imagens
src/preprocessing.py    # Validação, redimensionamento, ROI, cor
src/recognition.py      # CLIP zero-shot, limiares experimentais
src/visualization.py    # Desenho e composição gráfica
data/                   # Banco gerado automaticamente (fora do Git)
data_samples/           # Amostras/manifesto com autoria e licenças
assets/                 # Recursos da interface
tests/                  # Testes locais sem pesos de IA
docs/                   # Fontes, testes e declaração de uso de IA
requirements.txt        # Dependências completas
requirements-interface.txt # Instalação leve
.gitignore              # Exclui dados transitórios e ambiente
```

## Organização no GitHub

Cada integrante deve fazer alterações próprias identificáveis com commits e compreender
as partes centrais do código. Registrar fontes de fotos, dados técnicos, modelo CLIP,
licenças e uso de IA. Não inserir senhas nem chaves de API no repositório.

## Próximos passos

1. Executar o programa no computador da equipe.
2. Reunir fotos licenciadas e registrar em `data_samples/manifesto.csv`.
3. Testar o CLIP em fotos de todos os cinco modelos e em carros desconhecidos.
4. Ajustar recortes/prompt ou trocar de método se a acurácia for ruim.
5. Completar ano e versão do Opala SS, Uno e Fusca no catálogo.
6. Medir acurácia, rejeição de desconhecidos e latência; produzir apresentação.
