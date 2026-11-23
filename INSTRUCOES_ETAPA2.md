# AutoVision — Atualização experimental da Etapa 2

**Problema confirmado em 23/11/2026:** imagens sem carro e carros que não estão no catálogo podem receber classificações incorretas e altas pontuações relativas CLIP.

## O que foi alterado

- Adicionado `src/vehicle_detection.py`: antes de classificar, o YOLO11 nano verifica se existe um **automóvel** e devolve sua caixa no padrão XYXY.
- Adicionadas descrições de contraste em `src/recognition.py`: tentam identificar casos de carros de outros modelos. **Não oferecem rejeição universal**, especialmente em veículos não representados nos contrastes.
- A interface `app.py` analisa o recorte localizado pelo YOLO e mostra a caixa real de detecção. Mantém a seleção manual de ROI para imagens com múltiplos elementos.
- A estimativa de cor passou a considerar o recorte da caixa detectada, mas ainda não usa segmentação da carroceria.
- Adicionado `tests/test_open_set.py` para testar **regras de decisão** sem baixar pesos de IA.

## Como aplicar ao repositório existente

1. Faça uma cópia de segurança do projeto atual.
2. Extraia o ZIP da Etapa 2 **em uma pasta temporária**.
3. Copie somente os arquivos a seguir para a raiz do seu projeto no VS Code (substituindo quando solicitado):
   - `app.py`
   - `src/recognition.py`
   - `src/vehicle_detection.py` (novo)
   - `tests/test_open_set.py` (novo)
   - este documento `INSTRUCOES_ETAPA2.md`
4. Não substitua `.git`, `.gitignore`, `.venv`, `data/`, `README.md` nem o banco SQLite.
5. No terminal ativado `(.venv)`, execute:

```powershell
python -m pip install "ultralytics>=8.3,<9"
python -m pytest -q
python -m streamlit run app.py
```

6. Na primeira análise, o Ultralytics pode baixar `yolo11n.pt`. Para evitar enviar pesos ao GitHub, inclua na última linha do seu `.gitignore`:

```gitignore
*.pt
```

7. Refaça os testes: **casa, garagem vazia, árvore, Lamborghini, Opala SS, Fusca, Uno, Mustang, Porsche**. Observe que os escores do CLIP mudaram, pois agora há mais descrições concorrentes.
8. Envie as capturas dos resultados antes de fazer commit. Não use `git add .` enquanto houver modelo `.pt` sem a regra de exclusão.

## Limitações que não devem ser escondidas

- Detector YOLO pode produzir falsos positivos ou falsos negativos.
- Mesmo com YOLO, um carro fora dos cinco modelos pode ser rotulado como um dos cinco.
- As descrições de contraste são um **experimento**; exigem medição em veículos desconhecidos não usados para escolher esses textos.
- `96%` CLIP não significa `96%` de confiança estatística ou de precisão.
- A cor ainda é uma estimativa e deve ser avaliada separadamente.
- Pesos do Ultralytics precisam ter modelo e licença creditados; verificar termos de uso/AGPL na documentação oficial.
- Este pacote passou por testes estruturais locais, mas **o desempenho real do YOLO + CLIP ainda precisa ser verificado no computador do estudante**.
