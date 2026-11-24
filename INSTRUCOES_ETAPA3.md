# AutoVision — Atualização Etapa 3

**Objetivo:** selecionar qual automóvel analisar quando há vários, oferecer classificação manual de contingência quando YOLO falha e acrescentar descrições de contraste para New Beetle, Beetle moderno e GT3 RS de geração posterior.

## Aplicação segura no projeto existente (Windows / VS Code)

1. **Pare o Streamlit com `Ctrl+C`** no terminal em que está em execução.
2. Faça uma cópia de segurança da pasta principal, ou confira que tudo está salvo no GitHub. Não apague `.git`, `.venv`, `.gitignore` ou `data/`.
3. Extraia `AutoVision_Etapa3_atualizacao.zip` em uma pasta **temporária** (ex.: Downloads).
4. Copie o conteúdo da pasta temporária para a pasta principal que contém seu `app.py`, **mantendo a mesma estrutura**. Autorize substituir `app.py`, `src/recognition.py`, `src/vehicle_detection.py`, `src/visualization.py` e `requirements.txt`. As pastas `src`, `tests` e `docs` devem ser **mescladas**, não apagadas.
5. Nenhuma alteração de esquema do banco SQLite foi realizada. Não substitua seus registros ou `data/autovision.sqlite3`.
6. Confirme que o `.gitignore` contém `.venv/`, `*.pt` e `*.sqlite3` (o banco SQLite local não deve ser enviado para o GitHub).

No terminal PowerShell com `(.venv)` ativo:

```powershell
python -m pip install -r requirements.txt
python -m pytest -q
python -m streamlit run app.py
```

O novo `requirements.txt` inclui `ultralytics`; se já estiver instalado, o pip apenas verificará suas dependências. Os modelos podem ser baixados na primeira análise, se ainda não estiverem em cache.

## Como utilizar (mudança em relação à Etapa 2)

1. Carregue uma fotografia ou tire uma foto.
2. Se quiser restringir o campo de busca, ajuste a **região de interesse** por percentuais.
3. Clique em **Detectar veículos na imagem**. O YOLO encontra **todas** as caixas de classe `car` acima do limiar informado. A resolução pode ser alterada entre 480, 640 e 960.
4. Se o YOLO encontrar vários carros, escolha o número na caixa **Automóvel selecionado**. Os números também aparecem desenhados na imagem; a seleção recebe contorno amarelo.
5. Clique em **Analisar modelo selecionado** para enviar o recorte daquele veículo ao CLIP.
6. **Se o YOLO não encontrar o veículo:** marque **Classificar a região selecionada SEM exigir detecção YOLO** e confirme que seu recorte contém o carro. Isso contorna somente a etapa de detecção; é um resultado manual e menos verificado.
7. Após a classificação, abra o painel de **amostra de pintura** para selecionar uma pequena região da carroceria. Sem a amostra, a estimativa de cor continua sujeita a erros.

As classes de contraste de New Beetle, Beetle A5 e Porsche 991 **não entram no SQLite**. Elas apenas competem com as cinco categorias para tentar evitar confusões entre gerações. Isso não garante rejeição universal nem identificação do ano exato.

## Testes de regressão sugeridos

| Foto | Resultado desejado | Risco conhecido |
| --- | --- | --- |
| Fiat Uno vermelho em primeiro plano + BMW ao fundo | Escolher manualmente a caixa do Uno | YOLO pode não detectar o Uno |
| Fiat Uno que o YOLO não detectou | Selecionar recorte e usar modo manual | CLIP pode ser inconclusivo |
| New Beetle branco | Fora do catálogo ou inconclusivo | CLIP pode confundir com Fusca |
| Fusca clássico verdadeiro | Fusca clássico | Mudança nas descrições pode reduzir pontuações |
| Porsche GT3 RS 997.2 | Porsche cadastrado | Similaridade com gerações posteriores |
| Porsche GT3 RS 991 | Rejeitar / inconclusivo | Geração não é verificável com certeza |
| Opala SS de frente | Detecção após ajuste ou modo manual | Falha do YOLO para certos ângulos |
| Casa ou estacionamento vazio | Nenhum automóvel detectado | Modo manual ignora essa verificação |

### Como documentar os resultados

Use `docs/PLANO_TESTES.md` e um registro CSV com as colunas `imagem,modelo_real,grupo,detectou_yolo,carro_selecionado,modo_manual,resultado_clip,cor_estimada,tempo_yolo_s,tempo_clip_s,correto,observacoes`.

**Não confunda:** confiança do YOLO para a classe genérica *car*, pontuação relativa entre descrições do CLIP e acurácia calculada com imagens independentes.

## Antes de enviar ao GitHub

```powershell
git status
git add app.py src/recognition.py src/vehicle_detection.py src/visualization.py requirements.txt tests/test_stage3.py INSTRUCOES_ETAPA3.md
# Adicione também README.md e docs/ETAPA3_PLANO_TESTE.md, se aparecerem no git status.
git commit -m "Etapa 3: selecao de carros e fallback manual"
git push
```

É melhor primeiro conferir testes e comportamento real; execute commit/push somente após validar.
