# AutoVision — Etapa 4: fichas técnicas no SQLite

## Objetivo

Completar o catálogo sem alterar o YOLO, CLIP, parâmetros ou identificação visual da Etapa 3.1. Os cinco identificadores (`slug`) permanecem iguais. A atualização do banco é **automática** quando a aplicação inicia.

## Instalar com segurança no Windows / VS Code

1. Feche o Streamlit (`Ctrl + C`).
2. Faça backup do banco local, se existir:

   ```powershell
   if (Test-Path '.\data\autovision.sqlite3') { Copy-Item '.\data\autovision.sqlite3' '.\data\autovision.antes_etapa4.bak' }
   ```

3. Extraia o ZIP em pasta temporária e **substitua** somente `src/database.py` e `app.py` na raiz do AutoVision. **Adicione** `tests/test_database_stage4.py`, `docs/FONTES_FICHAS_TECNICAS.md` e este arquivo `INSTRUCOES_ETAPA4.md`. A estrutura de `src` e `tests` deve ser mesclada, nunca apagada.
4. Não substitua nem remova `.git`, `.gitignore`, `.venv`, `data/`, `imagens/`, `yolo11n.pt` ou outros arquivos existentes.
5. No terminal do VS Code, na raiz do projeto, execute:

   ```powershell
   .\.venv\Scripts\python.exe -m pytest -q
   .\.venv\Scripts\python.exe -m streamlit run app.py
   ```

6. Abra o menu **Catálogo**. As cinco fichas devem aparecer com período, motor, combustível, carroceria, potência, transmissão, tração e links para as fontes. Depois teste uma foto conhecida do Fusca ou Porsche: a mesma ficha será exibida no resultado.

## Avisos

- O projeto pode ter **mais testes** do que os apresentados aqui, se a equipe tiver criado arquivos adicionais.
- Se o banco tiver sido editado manualmente, as edições são preservadas e poderão aparecer em vez dos novos valores: isso é intencional. Compare com a documentação antes de alterar algo.
- O SQLite não é enviado ao GitHub: o código `src/database.py` gera/migra o banco automaticamente ao iniciar.
- **Não rode `git add .` nem faça commit sem verificar `git status` e os arquivos preparados.** Quando os testes reais passarem, registre um commit da Etapa 4.
- A pasta `imagens/` deve permanecer ignorada, inclusive em repositórios públicos.
