# AutoVision — fontes e critérios das fichas técnicas (Etapa 4)

## Regra de interpretação

- **Reconhecimento visual ≠ identificação exata de versão/ano.** O CLIP sugere o modelo e o banco apresenta características históricas da família/versão de referência.
- Informações como motorização, potência, tipo de combustível e câmbio **não são determinadas pela fotografia** quando o modelo teve diversas configurações.
- Potências em **hp** (Mustang) são valores históricos brutos de época, e **PS** (Porsche) são cavalos métricos; não comparar diretamente sem conversão e sem conhecer o método de medição.
- Fotografias e suas licenças são assunto separado deste catálogo de dados técnicos. Nenhuma imagem externa foi incluída no pacote.

## Fiat Uno de primeira geração — Brasil, 1984–2013

O Uno original iniciou sua fabricação brasileira em 1984 e encerrou sua produção em 2013. O **Novo Uno** foi apresentado em 2010 e é de outra geração. A família original compreende motores 1.0, 1.3, 1.5 e 1.6, além do Uno Turbo 1.4 (116 cv em 1994). Não atribuir um motor único a qualquer fotografia de Uno quadrado.

- Fiat/Stellantis: https://www.media.stellantis.com/br-pt/fiat/press/novo-uno-completa-15-anos-de-historia
- Quatro Rodas (Uno Mille): https://quatrorodas.abril.com.br/carros-classicos/fiat-uno-mille-historia-carro-popular-brasil/
- Quatro Rodas (linha do tempo): https://quatrorodas.abril.com.br/noticias/galeria-uno-30-anos/

## Volkswagen Fusca clássico — Brasil, 1959–1986 e 1993–1996

O Fusca original brasileiro teve produção em dois períodos. Existem variantes com boxer refrigerado a ar de 1.2, 1.3, 1.5 e 1.6 L; algumas versões brasileiras foram oferecidas a etanol. A produção global do Fusca clássico foi encerrada no México em 2003. **New Beetle** e **Beetle A5** são gerações diferentes e não estão cadastradas.

- Volkswagen: https://www.volkswagen-newsroom.com/en/the-volkswagen-beetle-a-success-story-2341/vw-beetle-through-the-years-2361
- Quatro Rodas (história brasileira): https://quatrorodas.abril.com.br/carros-classicos/do-sedan-ao-itamar-como-o-volkswagen-fusca-se-tornou-um-sucesso-no-brasil/
- Quatro Rodas (1600 etanol): https://quatrorodas.abril.com.br/carros-classicos/10-motivos-para-voce-nao-comprar-um-volkswagen-fusca/

## Chevrolet Opala SS — 1971–1980 (raríssimas unidades em 1981)

A linha SS existiu com diferentes carrocerias e motores. SS4 tinha configuração 2.5 L de quatro cilindros (151-S), e SS6 teve seis cilindros de 3.8/4.1 L (como o 250-S, oferecido a partir de 1976). Potências citadas são referências históricas de padrões diferentes: 98 cv brutos (151-S) e 153 cv líquidos (250-S). **Não comparar esses números diretamente**. Anos e versões podem variar.

- Quatro Rodas (história SS): https://quatrorodas.abril.com.br/carros-classicos/classicos-chevrolet-opala-ss-trouxe-esportividade-no-motor-4-1-e-no-visual/
- Quatro Rodas (potência e versões): https://quatrorodas.abril.com.br/carros-classicos/chevrolet-opala-ss-deixou-muito-esportivo-v8-para-tras-nos-anos-1970/
- AutoLivraria (151-S, potência bruta): https://autolivraria.com.br/bc/informe-se/passado/historia-chevrolet-opala-comodoro-diplomata-ss-caravan-2500-3800-4100/7/amp/

## Ford Mustang 1964½ — primeira série do ano/modelo 1965

O Mustang foi lançado em **17 de abril de 1964**. A versão inicial era hardtop ou conversível; o fastback passou a ser disponibilizado posteriormente. Motores de lançamento: 170 pol³ (seis em linha, 101 hp), V8 260 pol³ (164 hp), V8 289 pol³ (210 hp) e a opção 289 Hi-Po (271 hp, disponibilizada posteriormente em 1964). Os valores são históricos e não podem ser inferidos pela aparência.

- Ford (história oficial): https://www.ford.com/mustang/history/
- Reprodução de comunicado de lançamento da Ford, 13/04/1964: https://www.early-mustang.com/index.php/press-release

## Porsche 911 GT3 RS 2010 — geração 997.2

A referência cadastrada é o **GT3 RS 3.8 de 2010**, boxer de 6 cilindros, **450 PS**, câmbio manual de 6 marchas e tração traseira. O modelo não deve ser confundido com a família Porsche 911 em geral. O CLIP pode reconhecer um Porsche GT3 RS de geração posterior como esta referência; a aplicação não autentica o ano.

- Porsche (história da geração 997): https://newsroom.porsche.com/en/history/porsche-911-seven-generations-part-6-type-997-16489.html
- Porsche (especificações técnicas 2010, documento original): https://newsroom.porsche.com/dam/jcr%3Af3e401b7-b334-4442-a9b6-f719c3675d85/2010_911_GT3-RS_Specs.pdf.PDF

## Persistência no SQLite

O banco local `data/autovision.sqlite3` **não faz parte do GitHub**. Ao executar `init_db()`, o aplicativo atualiza as informações ainda iguais às fornecidas na versão inicial e inclui colunas novas. Valores personalizados pela equipe permanecem intactos. As fontes ficam na tabela `fontes_veiculos`, sem fotos externas.
