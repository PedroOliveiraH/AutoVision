# Fotografias de referência e teste — AutoVision

## 1. Objetivo

Esta pasta reúne fotografias de referência e imagens de exemplo utilizadas para demonstrar e avaliar o funcionamento do AutoVision, aplicação acadêmica de visão computacional desenvolvida com YOLO11 nano, CLIP, Streamlit e SQLite.

O sistema utiliza modelos de inteligência artificial pré-treinados. **Estas fotografias não constituem uma base de treinamento de um novo modelo**, sendo utilizadas para testes, exemplos visuais e demonstração da aplicação.

## 2. Organização das imagens

As fotografias estão organizadas conforme sua finalidade:

- **Referência do catálogo:** imagens dos modelos de veículos considerados no projeto.
- **Fora do catálogo:** veículos utilizados para verificar o comportamento diante de modelos não cadastrados.
- **Vários automóveis:** cenas destinadas à avaliação da localização e seleção de veículos.
- **Controle negativo:** imagens que permitem verificar o comportamento da detecção diante de cenas sem automóveis.

As imagens disponibilizadas nesta pasta não representam necessariamente o conjunto integral de fotografias utilizado na avaliação experimental apresentada no relatório técnico.

## 3. Fotografias dos modelos cadastrados

| Veículo de referência | Autor | Licença |
|---|---|---|
| Porsche 911 GT3 RS 2010 | MrWalkr | CC BY-SA 4.0 |
| Volkswagen Fusca clássico | Paixao 677 | CC BY-SA 4.0 |
| Ford Mustang — primeira geração | Alexander Migl | CC BY-SA 4.0 |
| Chevrolet Opala SS 1978 | Niemann333 | CC BY-SA 4.0 |
| Fiat Uno Turbo i.e. 1986 | Riley (NZ Car Freak) | CC BY 2.0 |

**Observação sobre o Mustang:** a fotografia `Ford_Mustang_I_IMG_3182.jpg` representa um Mustang de primeira geração. A página de origem não comprova que o exemplar pertença à série inicial informalmente conhecida como 1964½. Por esse motivo, a imagem não deve ser apresentada como comprovação desse ano ou dessa série específica.

As páginas individuais de origem estão identificadas no arquivo `manifest.csv`.

## 4. Fotografias complementares

| Imagem | Finalidade | Autor | Licença |
|---|---|---|---|
| Bugatti Veyron | Veículo fora do catálogo | Manju | CC BY-SA 3.0 |
| High Street, Narberth | Cena com vários automóveis | Jaggery | CC BY-SA 2.0 |
| Garagem com dois automóveis | Cena com vários automóveis | Ddgonzal | Domínio público |
| Volkswagen New Beetle 2006 | Veículo fora do catálogo | Vauxford | CC BY-SA 4.0 |
| Árvore de Socotra | Controle negativo | Alex38 | CC BY 4.0 |

Essas imagens permitem demonstrar situações em que o detector localiza vários veículos, em que a classificação deve rejeitar modelos desconhecidos e em que não se espera identificação de automóveis.

## 5. Direitos autorais e atribuição

As dez imagens documentadas no `manifest.csv` foram obtidas do Wikimedia Commons. Cada fotografia permanece sujeita à licença indicada em sua página original.

Este projeto não reivindica autoria sobre as fotografias de terceiros.

Para imagens sob licenças **Creative Commons Attribution (CC BY)**, deve-se identificar o autor, indicar a licença e fornecer a referência da obra original, além de informar eventuais alterações.

Para imagens sob licenças **Creative Commons Attribution-ShareAlike (CC BY-SA)**, aplicam-se também as condições de compartilhamento de adaptações sob licença igual ou compatível.

A fotografia da garagem possui uma declaração de disponibilização em domínio público pelo titular dos direitos.

### Links das licenças

- [CC BY 2.0](https://creativecommons.org/licenses/by/2.0/)
- [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/)
- [CC BY-SA 2.0](https://creativecommons.org/licenses/by-sa/2.0/)
- [CC BY-SA 3.0](https://creativecommons.org/licenses/by-sa/3.0/)
- [CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/)

O arquivo `manifest.csv` contém os nomes originais dos arquivos, a autoria informada, a página da fotografia no Wikimedia Commons e a licença correspondente.

Caso uma imagem seja recortada, editada ou modificada para apresentação, a alteração deverá ser identificada nos créditos.

## 6. Limitações e cuidados

A identificação visual de um automóvel não comprova seu ano de fabricação, versão, motorização ou originalidade.

As imagens de referência foram escolhidas considerando características visuais dos veículos. O sistema pode produzir resultados corretos, inconclusivos ou incorretos.

As fotografias documentadas nesta pasta não devem ser confundidas com um conjunto independente de validação estatística. Os resultados experimentais oficiais do projeto estão descritos no relatório técnico, com identificação das categorias de teste, quantidade de avaliações e limitações metodológicas.

## 7. Registro de procedência

O arquivo `manifest.csv` utiliza os campos:

- `arquivo`: nome exato da fotografia.
- `veiculo_slug`: identificador do catálogo, quando aplicável e confirmado.
- `finalidade`: função da imagem no projeto.
- `angulo`: perspectiva visual ou tipo de cena.
- `autor`: autoria indicada na página de origem.
- `origem_url`: link da página individual no Wikimedia Commons.
- `licenca_ou_autorizacao`: condição de reutilização declarada.

Antes de adicionar novas imagens ao repositório público, a equipe deverá verificar sua origem e licença.

## 8. Projeto acadêmico

**Projeto:** AutoVision — Detecção e reconhecimento de automóveis  
**Disciplina:** Computação Gráfica  
**Professor:** Pedro Cândido  
**Integrantes:** Pedro Henrique Melgaço de Oliveira e Matheus Gonçalves Marques

**Repositório:** https://github.com/PedroOliveiraH/AutoVision

As imagens são utilizadas para fins de documentação, experimentação e demonstração acadêmica, respeitando as condições de suas respectivas licenças.