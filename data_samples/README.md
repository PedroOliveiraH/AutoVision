# Fotografias de referência e teste

Organizar por modelo e separar desenvolvimento, validação e teste.
A aplicação inicial não precisa dessas fotos para a inferência zero-shot, mas elas
são indispensáveis para medir qualidade e comparar os métodos.

Modelo sugerido de organização:

- dev/fiat-uno/
- dev/volkswagen-fusca/
- dev/chevrolet-opala-ss/
- dev/porsche-911-gt3-rs-2010/
- dev/ford-mustang-1964-meio/
- validacao/... (não usar imagens repetidas)
- teste/... (não usar imagens repetidas)
- teste/desconhecidos/

Preencher o manifesto.csv antes de usar as imagens na avaliação.
