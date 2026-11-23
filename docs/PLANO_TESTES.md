# Plano de testes — AutoVision

## O que testar

1. Carro conhecido, fotografia frontal.
2. Carro conhecido, fotografia lateral ou traseira.
3. Outra cor e iluminação.
4. Dez fotos de veículos que não pertencem às cinco categorias.
5. Foto sem carro.
6. Arquivo inválido.
7. Tempo de execução da classificação em CPU, após o modelo carregado.

## Dados e separação

Usar fotos de teste **não empregadas** para ajustar prompts, limiares nem escolher o algoritmo.
Meta piloto: 5 fotos independentes de teste por modelo (25), além de 10 fotos de desconhecidos.
Separar desenvolvimento, validação e teste final; preservar a origem e licença.

## Métricas

- Acurácia = classificações corretas / total de fotos com classe verdadeira conhecida.
- Matriz de confusão: comparação entre classe real e classe prevista (incluindo 'inconclusivo').
- Taxa de rejeição de desconhecidos = desconhecidos rejeitados / total de imagens de desconhecidos.
- Latência média (segundos por imagem), após aquecimento do modelo, com descrição do hardware.

**Os valores ainda precisam ser medidos.** Não relatar porcentagens ou acertos não verificados.
