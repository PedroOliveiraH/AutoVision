# AutoVision — Correção pontual 3.1 (base: Etapa 3)

## O que muda

1. Em `src/recognition.py`, a descrição de contraste do Porsche 991 (que entrou na Etapa 3 e passou a disputar pontuação com o GT3 RS 997.2) foi retirada **temporariamente** da classificação geral. Essa mudança tenta recuperar o reconhecimento do Porsche 997.2 observado antes, mas **não garante reconhecimento correto da geração** e pode permitir que um Porsche 991 também seja confundido com o 997.2. O CLIP não verifica ano de fabricação por fotografia.
2. Mensagens de recusa e de sugestão deixam de afirmar que existe um carro no **modo manual**. Se o YOLO não confirmou a presença, a interface não faz essa afirmação.
3. Para uma correspondência com o Porsche cadastrado, a interface ressalta que o ano de 2010 e a geração 997.2 não são confirmados automaticamente.

Nenhuma modificação nos módulos YOLO, OpenCV e SQLite. Não há bibliotecas novas.

## Instalação no projeto já atualizado para Etapa 3

1. Feche o Streamlit com `Ctrl+C` no terminal.
2. Faça uma cópia de segurança dos arquivos que serão alterados.
3. Extraia o ZIP em pasta temporária.
4. Copie `app.py`, `README.md` e `INSTRUCOES_CORRECAO_ETAPA3_1.md` para a **pasta principal** do AutoVision.
5. Copie `src/recognition.py` para `src/`, substituindo apenas esse arquivo.
6. Copie `tests/test_stage3.py` e `tests/test_hotfix_stage3_1.py` para `tests/`.
7. Não copie o ZIP inteiro para dentro do projeto; copie os arquivos nas pastas correspondentes. Não exclua `data/`, `.git/`, `.venv/`, `imagens/`, `.gitignore` ou `yolo11n.pt`.

## Comandos no PowerShell do VS Code (pasta principal do projeto)

```powershell
.\.venv\Scripts\python.exe -m pytest -q
.\.venv\Scripts\python.exe -m streamlit run app.py
```

Resultado esperado dos testes de lógica deste pacote, junto com as Etapas 1–3: **25 passed**. O número pode variar se houver testes locais adicionais.

## Verificações com imagens reais — obrigatórias antes do commit

Use os mesmos parâmetros YOLO 0.30, 640 px, CLIP 0.55, margem 0.10, e o mesmo recorte de cada fotografia (salvo se estiver testando explicitamente o recorte).

- **Porsche 997.2 cinza-escuro com rodas vermelhas:** foto que a Etapa 2 reconhecia e a Etapa 3 rejeitou. Verifique se a sugestão do modelo voltou. Não altere as configurações para forçar o resultado.
- **Porsche preto:** verifique a geração real da foto antes de considerar a classificação correta ou incorreta.
- **Porsche 991 de 2015, se disponível:** teste para verificar se a retirada do contraste causou uma falsa aceitação do 997.2. Se aceitar, registre a limitação. **Não apresente ano exato como confirmado**.
- **Beetle A5 branco e Fusca clássico:** confira se a separação observada na Etapa 3 continua funcionando.
- **Árvore no modo manual:** a tela não deve afirmar que há um carro. Ao testar de propósito uma entrada inválida, evite interpretar a caixa de confirmação do usuário como prova de detecção.

Registre foto/origem, resultado e pontuações, inclusive os erros. Os 25 testes automatizados não medem a qualidade de CLIP nem YOLO com imagens reais.

## Controle de versão

**Somente após validar:**

```powershell
git status
git add app.py README.md INSTRUCOES_CORRECAO_ETAPA3_1.md src/recognition.py tests/test_stage3.py tests/test_hotfix_stage3_1.py
git commit -m "Etapa 3.1: corrige mensagens manuais e revisa contraste Porsche"
git push origin main
```

Os arquivos locais de imagem permanecem ignorados; não use `git add .` sem inspecionar o status.
