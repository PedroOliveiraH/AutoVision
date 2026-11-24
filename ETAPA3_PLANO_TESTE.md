# AutoVision — Guia de validação da Etapa 3

Este é um protocolo de teste, **não** um relatório de resultados já medidos.

## Diferenciar três objetivos

- **Detecção:** YOLO encontrou o carro correto? Se houver vários, o usuário conseguiu selecionar o pretendido?
- **Classificação:** quando o recorte contém o carro desejado, o CLIP sugere a categoria do catálogo ou rejeita?
- **Cor:** houve acerto usando imagem inteira, caixa YOLO ou amostra selecionada da pintura?

## Registro mínimo

Para cada foto, salve a origem/licença, modelo real, geração conhecida, se a imagem foi usada para desenvolver ou testar, parâmetros YOLO/CLIP, tempo e resultado. Não reutilize a mesma foto de desenvolvimento como evidência de desempenho final. Considere testes com carro de outro modelo, outra geração e cenário sem carro.

## Cenários indispensáveis

1. Uno e BMW na mesma foto: escolher a caixa correspondente ao Uno.
2. Uno vermelho que passou despercebido: usar modo manual sem esconder que o YOLO falhou.
3. Fusca Type 1, New Beetle e Beetle A5: separar acerto e falsas aceitações.
4. GT3 RS 997.2 e GT3 RS 991: verificar confusões entre gerações.
5. Opala SS visto de frente e de perfil: registrar falhas de detecção ou classificação.
6. Casa/estacionamento vazio: rejeição de presença; não usar fallback manual como se fosse validação.
7. Cor: escolher uma área sem vidros, pneus ou adesivos e comparar com o rótulo visual.

## Métricas recomendadas

- **Taxa de detecção** = fotos com carro e detecção do carro de interesse / fotos com carro.
- **Acurácia de ponta a ponta** = fotos dos cinco modelos em que o sistema detectou e classificou corretamente / total de fotos avaliadas desses modelos.
- **Taxa de rejeição dos desconhecidos** = fotos de outros veículos corretamente rejeitadas / total de desconhecidos.
- **Taxa de falsas aceitações** = fotos de outros veículos classificadas como um dos cinco / total de desconhecidos.
- **Latência média (sem aquecimento inicial)** = média dos tempos de detecção + classificação, executando sempre nas mesmas condições.

Relate separadamente os casos em **modo manual**, que não comprovam a detecção automática. O resultado do CLIP para um carro de outro ano/modelo não comprova o ano correto.
