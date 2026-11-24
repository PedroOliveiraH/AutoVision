# Refinamento 4.2 — distinção experimental Porsche 997 × 991

## Motivação

Um Porsche GT3 RS 991 foi associado à ficha do Porsche 911 GT3 RS 2010 (997.2). Na Etapa 3, inserir o 991 como concorrente no ranking geral fez exemplos da geração 997.2 perderem o primeiro lugar. Por isso, o refinamento usa uma comparação **apenas após** uma sugestão primária de Porsche.

## Protocolo

1. Classificador geral zero-shot CLIP compara os cinco carros e contrastes para desconhecidos.
2. Se o primeiro colocado for o Porsche cadastrado, comparar uma segunda vez quatro descrições: duas da família 997 e duas da família 991.
3. Somar e normalizar as pontuações por família. Como as classes são descrições textuais, **não** interpretar como probabilidade calibrada.
4. Usar uma **margem de separação exploratória de 0,25**, que deve ser validada com fotos independentes. Se não houver diferença suficiente, indicar geração inconclusiva. Se 991 for favorecida, **não** exibir a ficha de 2010.
5. Reportar limitações: distinção 997 × 991 não implica reconhecer ano de fabricação nem 997.1 × 997.2.

## Referências de especificações e estilo

- Porsche, "How fast is a Porsche 911 GT3 RS?" — GT3 RS 997.2: 450 PS; GT3 RS 991.1: 500 PS. https://www.porsche.com/stories/mobility/how-fast-porsche-911-gt3-rs/
- Porsche Newsroom, "The 911 GT3 RS: the race car for the circuit racetrack and everyday driving" — estreia da geração 991 em 2015. https://newsroom.porsche.com/en/products/porsche-911-gt3-rs-race-car-circuit-racetrack-everyday-driving-2015-10051.html
- Folheto Porsche 911 GT3 RS 2015 — características aerodinâmicas incluindo entradas de ar laterais. https://www.auto-brochures.com/makes/Porsche/911/Porsche_int%20911GT3-RS_2015.pdf

## Riscos e limitações

- Prompts podem errar a geração dependendo de ângulo, resolução, cor, aerofólio e modificações do veículo.
- A margem 0,25 não foi calibrada estatisticamente.
- Verificar sempre em imagens não usadas para ajustar as descrições.
- Testes unitários cobrem o *código de decisão*, e não a acurácia real do CLIP.
