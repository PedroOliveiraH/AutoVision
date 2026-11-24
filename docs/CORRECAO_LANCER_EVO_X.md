# AutoVision — Refinamento 4.1: falso positivo Lancer → Porsche

## Problema observado (fotografia de desenvolvimento)

Uma foto da traseira de um Mitsubishi Lancer Evolution X verde, com aerofólio grande, foi enviada ao modo manual porque o YOLO não encontrou automóveis. O CLIP classificou equivocadamente o recorte como Porsche 911 GT3 RS (997.2), que pertence ao catálogo. O erro é de **identificação do modelo**; a falha do YOLO é independente.

## Hipótese e mudança

O CLIP `openai/clip-vit-base-patch32` compara uma imagem com *descrições textuais fornecidas*. A lista anterior tinha descrições de SUV, hatch e supercarro, mas não incluía um Lancer nem sedãs esportivos modernos semelhantes. A presença de aerofólio podia contribuir para aproximar o Lancer do Porsche.

Adicionadas duas **classes de contraste**, sem alterar os cinco veículos cadastrados:

- `fora-lancer-evo-x`: `a Mitsubishi Lancer Evolution X four door Japanese performance sedan with a large rear wing`
- `fora-seda-esportivo`: `a modern modified four door sports sedan with a large rear spoiler`

A função de decisão existente já rejeita a imagem quando o melhor rótulo é de contraste. **Não foi criada uma ficha técnica para o Lancer.** As descrições são genéricas no que diz respeito à cor para não depender apenas do Lancer verde do teste.

## Limitações

Esta mudança corrige a *cobertura das alternativas textuais*, mas **não garante** rejeitar o Mitsubishi ou qualquer carro fora do catálogo. Os escores do CLIP são relativos a todas as classes oferecidas e não são probabilidades calibradas. Inserir rótulos muda a normalização do ranking, podendo inclusive prejudicar acertos anteriores. Os testes automatizados apenas verificam a lógica e a presença dos rótulos. Não substituem uma avaliação com imagens.

## Teste exploratório de verificação

Manter os controles que já foram usados na interface (**limiar YOLO 0,30, pontuação CLIP 0,55, margem 0,10, resolução 640**), caso permaneçam adequados. Testar sempre o mesmo recorte anterior, e depois fotografias independentes.

| Caso | Esperado | Registrar |
| --- | --- | --- |
| Lancer Evolution X verde, traseira, usando modo manual | Rejeição como fora do catálogo, preferencialmente `fora-lancer-evo-x` ou `fora-seda-esportivo` na primeira posição | Primeiro rótulo, pontuação, resultado, imagem e modo |
| Outro Lancer Evolution X, outro ângulo/cor (imagem inédita) | Rejeição como fora do catálogo | Resultado sem ajuste de parâmetros |
| Porsche GT3 RS 997.2 cinza/rodas vermelhas | Reconhecimento do modelo do catálogo | Pontuação e resultado |
| Porsche GT3 RS 997.2 laranja | Reconhecimento do modelo do catálogo | Pontuação e resultado |
| Fusca clássico | Reconhecimento como Fusca | Resultado |
| Carro desconhecido (ex. sedã moderno) | Rejeição | Resultado |

**Se o Lancer ainda for classificado como Porsche:** não declarar que a correção funcionou, não acrescentar filtros baseados na cor ou fotografia específica e não reduzir o limiar apenas para obter o resultado desejado. Guardar a pontuação de todos os rótulos e comparar também as duas fotografias de Porsche. Uma próxima abordagem seria avaliar embeddings e limiares sobre um conjunto de validação separado.

## Arquivos da atualização

Somente `src/recognition.py` substituído e `tests/test_lancer_contrastes.py` adicionado, além desta documentação e instruções de instalação. YOLO, Streamlit, banco SQLite, fichas técnicas e demais arquivos permanecem inalterados.
