# Reversede L1 — relatório de implementação local privada

Data da verificação: 2026-10-12
Escopo: fundação privada, preservação, portabilidade inicial, hardening e validação local.

## Estado final

- `IMPLEMENTATION_STARTED: YES`
- `L1_STATUS: COMPLETE`
- `GIT_INITIALIZED: NO`
- `REMOTE_OPERATIONS: NO`
- `PUBLICATION: NO`
- `GITHUB_PRIVATE_GATE: PREPARED — NOT EXECUTED`
- `PUBLIC_RELEASE: OUT OF SCOPE`
- `PUBLIC_DISCLOSURE: USER-CONTROLLED`

A implementação ocorreu somente nesta cópia irmã. A árvore preservada do estudo
não foi usada como diretório de trabalho. Nenhum benchmark das Fases 0–5, holdout
ou experimento científico foi reexecutado.

## Contrato preservado

- distribuição: `reversede-ai`;
- import principal: `reversede`;
- API pública: `Reversede`, `ReversedeConfig`;
- layout: `src/`;
- versão de trabalho: `0.3.0.dev0`;
- adaptador temporário: `reverseda_ai.ReversedaAutonoma`;
- estudo histórico: execução `0.2.0`, sem reatribuição para `0.3.0.dev0`.

## Alterações implementadas

Arquivos adicionados:

- `.gitignore`
- `AUTHORS.md`
- `SECURITY.md`
- `docs/compatibility.md`
- `examples/quickstart.py`
- `provenance/INCLUSION_POLICY.md`
- `provenance/SOURCE_SNAPSHOT.json`
- `tests/test_hardening.py`
- este relatório e o manifesto final de hashes

Arquivos modificados em relação à cópia preservada:

- `.github/workflows/ci.yml`
- `CHANGELOG.md`
- `CONTRIBUTING.md`
- `MANIFEST.in`
- `README.md`
- `docs/api_reference.md`
- `docs/architecture.md`
- `docs/licensing_and_provenance.md`
- `docs/quickstart.md`
- `src/reversede/api.py`
- `src/reversede/blueprint.py`
- `src/reversede/types.py`

O hardening acrescentou serialização de valores nulos e escalares NumPy/pandas,
tratamento consistente de números com vírgula decimal, conversão temporal sem a
API `view` descontinuada, propagação dos limites configuráveis ao blueprint,
normalização segura de categorias mistas e proteção contra injeção por alertas
multilinha no código gerado. Os novos testes cobrem também determinismo em
empates, configuração efetiva, não mutação do input e serialização JSON.

## Evidências de preservação

- snapshot pré-implementação: 32 arquivos, 0 ausentes e 0 divergências;
- manifesto congelado das Fases 0–5: 115 entradas, 100 hashes idênticos,
  0 ausentes e as mesmas 15 divergências históricas já atribuídas à Fase 7;
- PDF do manuscrito:
  `4a3736ab5edb7507d20288478bfd8a51d7ac4c82d15a0898b3ac5d267ef152aa`;
- os quatro documentos de preparação foram incluídos no snapshot antes da
  edição e não foram alterados nesta etapa;
- dados, PDFs, manuscrito, predições, splits, métricas, notebooks, ambientes e
  relatórios científicos não foram copiados para esta biblioteca.

## Verificações executadas

### Baseline

- primeira invocação de pytest: 17 testes aprovados e 1 erro de preparação por
  resolução incorreta do diretório temporário; não houve falha funcional;
- repetição com caminho temporário absoluto: `18 passed in 2.33s`.

### Estado L1

- pytest final: `23 passed in 2.72s`;
- execução com cobertura: `23 passed in 22.19s`;
- cobertura informativa: 645 statements, 51 não cobertos, total 92%;
- `ruff check --no-cache src tests examples`: aprovado;
- `ruff format --check --no-cache src tests examples`: 20 arquivos formatados;
- exemplo sintético local: executado sem rede e sem dados externos;
- wheel instalado com `pip --target --no-deps --no-index`: aprovado;
- sdist instalado com `pip --target --no-deps --no-index --no-build-isolation`:
  aprovado;
- import dos dois artefatos confirmado a partir de seus destinos isolados;
- núcleo com imports de `sklearn` e SciPy deliberadamente bloqueados: aprovado;
- blueprint executado com scikit-learn já instalado, incluindo `fit_transform`
  e `transform`: aprovado;
- `twine check` no wheel e no sdist: aprovado;
- auditoria estática da árvore e dos dois arquivos de distribuição: nenhum dado,
  PDF, cache, ambiente, caminho pessoal ou indicador comum de segredo encontrado.

O comando padrão `python -m build --no-isolation` não produziu artefatos porque
o ambiente existente não continha a dependência de build `wheel`. Nenhuma
dependência foi instalada. O wheel foi então produzido por `pip wheel --no-deps
--no-build-isolation --no-index`, e o sdist pelo backend local
`setuptools.build_meta`, usando somente componentes já presentes. Os dois foram
validados, auditados e instalados como descrito acima.

## Artefatos locais, não publicados

- `reversede_ai-0.3.0.dev0-py3-none-any.whl`
  bytes: 24.358
  SHA-256: `9e48c9675dff45c54bcb91b3cd3421e0d747d061abbc063a48d32d598d57f05f`
- `reversede_ai-0.3.0.dev0.tar.gz`
  bytes: 33.192
  SHA-256: `ef761b9f3d2581d7f8ffd7c48511be2d0e232d3a2471f58d5803a3468a7e26aa`

Os artefatos estão fora da árvore da biblioteca, no diretório de preparação.
O wheel contém 21 arquivos e o sdist 42; ambos tiveram zero achados nas regras
de nomes proibidos, caminhos pessoais e indicadores comuns de segredo.

## Limitações e itens não testados

- CI remota não foi executada; o workflow é somente uma configuração preparada;
- Linux, macOS e Python 3.10, 3.11 e 3.13 não foram executados localmente;
- Google Colab, Jupyter, VS Code, PyCharm e Anaconda/Conda não foram executados;
- o adaptador opcional `ydata-profiling` não foi exercitado em carga real;
- não houve benchmark de desempenho nem repetição do estudo científico;
- não foi testada reprodutibilidade binária bit a bit entre builds;
- nenhuma auditoria jurídica definitiva de autoria, copyright ou licenças de
  terceiros foi concluída;
- nenhum repositório Git ou GitHub foi criado, e controle de acesso remoto não
  foi configurado.

## Condição de parada

A Etapa L1 termina aqui. Qualquer inicialização Git, criação de repositório
GitHub privado, execução de CI remota, publicação ou novo experimento exige uma
autorização separada do usuário.
