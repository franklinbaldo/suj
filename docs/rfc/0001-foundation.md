---
type: RFC
number: 1
status: proposed
date: 2026-08-12
title: Fundação arquitetural do suj
author: Franklin Baldo
---

# RFC 0001 — Fundação arquitetural do `suj`

## Resumo

O `suj` será um servidor MCP experimental para pesquisa sobre serviços
disponíveis por `jus.br`. Ele nasce explicitamente não oficial, potencialmente
inseguro e inadequado para processos reais.

Este RFC estabelece a base antes da primeira integração. A decisão central é:

> FastMCP é a superfície pública e o framework de aplicação; o código próprio
> do `suj` deve representar apenas o domínio observado, os protocolos remotos e
> as garantias de segurança que o FastMCP não conhece.

A primeira versão será offline e somente leitura. Autenticação real, consulta
remota e qualquer escrita dependerão de RFCs posteriores e independentes.

## Motivação

Uma análise dos repositórios irmãos [`pink`](https://github.com/franklinbaldo/pink)
e [`todos`](https://github.com/franklinbaldo/todos) mostra que os refactors mais
caros não vieram da lógica HTTP. Vieram de decisões estruturais que atravessaram
todo o catálogo:

1. registros, decorators e schemas paralelos ao FastMCP;
2. singleton global e registro por efeito colateral de importação;
3. tools misturadas com clients, CLI e composição;
4. retornos `dict`, sentinels e envelopes de sucesso/erro;
5. confirmação declarativa sem enforcement no ponto do efeito;
6. escrita considerada bem-sucedida sem pós-condição observada;
7. mocks preservando formatos antigos e escondendo falhas reais;
8. gates de qualidade adicionados depois que a dívida já estava espalhada.

O `pink` precisou remover seu mini-framework de tools, o registry global, o
singleton FastMCP e bridges de output para voltar a uma composição nativa. O
`todos` documenta a mesma direção em sua RFC 0035: tool, schema, DI, middleware,
transforms e lifecycle devem vir do FastMCP; código próprio deve ficar restrito
à semântica do sistema integrado.

## Objetivos

- manter uma única fonte de verdade para o catálogo MCP;
- separar transporte MCP, casos de uso e protocolo remoto;
- publicar contratos Pydantic desde a primeira resposta composta;
- tornar ausência, falha, submissão e verificação estados distintos;
- impedir efeitos externos por default e por construção;
- permitir testes integralmente offline com fixtures sintéticas;
- manter o catálogo pequeno, auditável e estável;
- criar gates antes de existir dívida histórica.

## Não objetivos

- ser SDK oficial ou completo do `jus.br`;
- prometer estabilidade de endpoints não documentados;
- automatizar SSO, certificado digital ou desafio humano;
- aceitar credenciais ou dados processuais reais na fase inicial;
- reproduzir toda a interface web;
- criar framework próprio de tools, operations, capabilities ou workflows;
- oferecer compatibilidade preventiva com consumidores inexistentes.

## Princípios normativos

Os termos **DEVE**, **NÃO DEVE** e **PODE** são normativos.

### 1. FastMCP-first

- A função Python publicada como tool é a unidade pública executável.

- O FastMCP DEVE derivar input schema, output schema e structured content.

- O default do FastMCP DEVE ser aceito sempre que satisfizer o requisito. Não
  configuraremos preventivamente comportamento que ainda não causou um
  problema concreto.

- Quando o default não bastar, a ordem obrigatória de decisão será:

  1. default do FastMCP sem customização;
  2. opção de configuração nativa;
  3. annotation, tag ou dependency injection nativa;
  4. middleware, transform, provider ou lifespan nativo;
  5. adapter mínimo de domínio;
  6. código de infraestrutura próprio, somente com lacuna demonstrada.

- Pular uma etapa exige registrar no PR o requisito não atendido e o teste que
  demonstra a lacuna.

- O projeto NÃO DEVE criar registry, decorator, descriptor `Operation`, schema
  resolver, envelope MCP ou protocolo de tool paralelo.

- Metadata local reutilizável PODE existir apenas como constantes nativas do
  MCP/FastMCP, sem formar um segundo catálogo.

Essa heurística também vale para decisões aparentemente pequenas. O `suj` não
deve customizar serialização, tratamento de erro, descoberta, CLI, transporte,
logging ou lifecycle apenas para antecipar uma necessidade possível. Defaults
reduzem superfície de manutenção e acompanham as correções do framework.

### 2. Composição explícita e sem estado global

`build_mcp()` será o único composition root e criará uma instância nova:

```text
CLI/stdio ──> build_mcp()
testes    ──> build_mcp()
introspecção -> build_mcp()
```

- Importar módulos NÃO DEVE registrar tools por efeito colateral.
- Não haverá singleton MCP mutável.
- Tools serão reunidas explicitamente em módulos de capability.
- Duplicidade de nome DEVE falhar durante a composição.
- Duas chamadas consecutivas a `build_mcp()` DEVEM produzir catálogos
  estruturalmente idênticos e servidores independentes.

Recursos compartilhados serão inicializados por lifespan nativo do FastMCP,
sempre com cleanup em `try/finally`. Dependências por request serão declaradas
com `Depends()`; por serem injetadas, não aparecem no schema que o agente vê.
Não criaremos service locator ou contexto próprio para substituir esses dois
mecanismos.

### 3. Fronteiras de código

```text
src/suj/
├── mcp/          # composição, middleware e entrypoint
├── tools/        # adapters finos da superfície pública
├── application/  # casos de uso, sem dependência de MCP
├── domain/       # modelos, estados, erros e políticas
├── jus/          # client e DTOs do protocolo remoto observado
└── settings.py   # configuração não secreta
```

- `tools/` NÃO DEVE conter HTTP, parsing ou custódia de credencial.
- `application/` NÃO DEVE importar FastMCP.
- `jus/` NÃO DEVE conhecer nomes de tools ou envelopes MCP.
- Um adapter em `tools/` só existe quando a assinatura pública realmente
  difere do caso de uso. Wrappers 1:1 são proibidos.

### 4. Contratos de retorno

- Toda resposta pública composta DEVE ser um `BaseModel` Pydantic explícito.
- Tools NÃO DEVEM retornar `dict[str, Any]`, tuplas posicionais, `None` como
  erro ou strings mágicas de status.
- Falhas esperadas DEVEM ser exceções tipadas e chegar ao MCP como falha, não
  como conteúdo de uma resposta bem-sucedida.
- Não haverá `{"ok": true}` ou `{"error": ...}` genérico. Um retorno normal já
  representa sucesso; um erro usa o canal de erro.
- Resultados com variantes reais DEVEM usar união discriminada.
- Nomes wire serão definidos uma vez no modelo e testados contra o schema
  publicado.
- O default de dereference de schemas do FastMCP será mantido. Só será
  desabilitado se um consumidor real demonstrar suporte correto a `$ref` e o
  ganho de tamanho justificar a divergência.
- `ToolResult` só será usado quando houver necessidade concreta de combinar
  content blocks, structured content e metadata. O default permanece retornar
  diretamente o modelo tipado.

### 5. Verdade sobre estado remoto

Uma requisição HTTP aceita não prova que o efeito existe no sistema remoto.
Respostas de escrita futuras deverão distinguir:

- `prepared`: efeito ainda não enviado;
- `submitted`: requisição aceita, efeito final não verificado;
- `verified`: pós-condição observada por leitura independente;
- `indeterminate`: não foi possível determinar se o efeito ocorreu.

O `suj` NÃO DEVE afirmar `verified` com base apenas na resposta do POST. Recibo,
identificador remoto e pós-condição são evidências diferentes e devem ocupar
campos diferentes.

### 6. Escrita real é uma capability futura

Nenhuma tool de escrita remota fará parte da fase inicial. Sua introdução
exigirá RFC própria contendo, no mínimo:

1. evidência reproduzível do protocolo;
2. modelo de ameaça;
3. preview e payload canônico;
4. confirmação vinculada ao hash exato do payload, não um `bool` genérico;
5. expiração e uso único da confirmação;
6. gate global de escrita desabilitado por default;
7. política de retry e idempotência;
8. pós-condição e estado `indeterminate`;
9. recibo e trilha de auditoria sem segredos ou dados pessoais;
10. testes provando que todo caminho sem autorização para antes do primeiro
    byte de uma requisição de escrita.

`destructiveHint` é informação para o host; NÃO é enforcement suficiente.

Em stdio, os checks OAuth de autorização do FastMCP não são executados porque
esse transporte não possui contexto OAuth. Portanto, uma policy de escrita do
`suj` nunca poderá depender deles. Se houver transporte HTTP no futuro,
autenticação e autorização usarão providers e auth checks nativos do FastMCP,
mas continuarão complementares às garantias executáveis de domínio.

### 7. HTTP deliberado

- Um único client assíncrono será criado no lifespan e injetado nos casos de
  uso; não haverá client global criado no import.
- Toda chamada terá timeout explícito.
- Retries automáticos serão limitados a leituras idempotentes e falhas
  transitórias conhecidas.
- Escritas NÃO terão retry automático sem chave de idempotência comprovada.
- Redirects, hosts permitidos e limites de tamanho serão políticas explícitas.
- DTO remoto e modelo público serão tipos diferentes quando suas semânticas
  diferirem; o formato acidental do upstream não será o contrato MCP.
- Toda tool que possa esperar rede terá `timeout` nativo do FastMCP, além dos
  timeouts de conexão/leitura/escrita do HTTPX.
- Um deployment HTTP deverá configurar explicitamente hosts e origins
  confiáveis. Não dependerá do comportamento default de uma patch release para
  proteção contra DNS rebinding.

### 8. Credenciais

- Segredos não pertencem a `Settings`, `.env`, argumentos de tool, logs,
  fixtures ou responses.
- O keyring terá service name exclusivo (`suj`) e chaves versionáveis apenas
  quando uma migração for necessária.
- Tokens serão relidos no uso; um token removido ou substituído não pode ficar
  vivo indefinidamente em cache global.
- O `suj` não automatizará login, SSO, certificado ou renovação enquanto só
  possuir um Bearer observado manualmente.
- Expiração será reportada honestamente; ausência e expiração serão erros
  distintos.

Erros inesperados serão mascarados na fronteira MCP. Somente erros de domínio
deliberadamente seguros para o agente serão convertidos em `ToolError`; detalhes
internos continuam disponíveis apenas em logging redigido.

### 9. Dados e privacidade

- Fixtures DEVEM ser sintéticas e conter marcadores explícitos de ficção.
- Respostas reais nunca serão versionadas, nem depois de anonimização ad hoc.
- Logs usarão allowlist de campos; body, Authorization, cookies, documentos,
  nomes, CPF/CNPJ e números de processo não serão registrados por default.
- Testes deverão procurar padrões de segredo e identificadores no corpus
  versionado.

### 10. Catálogo e nomes

O nome da tool descreve a operação de domínio, não o endpoint nem a tecnologia.
A forma preferida é `<recurso>_<verbo>`:

- `suj_status`
- `processo_consultar`
- `peticao_preparar`
- `peticao_protocolar`
- `peticao_recibo_obter`

Uma operação que mistura leitura e escrita deve ser dividida. Aliases de
compatibilidade só poderão existir para consumidores reais identificados.

O catálogo será pequeno. Antes de adicionar uma tool, deve-se provar que ela
representa capability distinta, e não apenas outra combinação de parâmetros.

### 11. OKF para conhecimento e dados

O repositório será um bundle Open Knowledge Format (OKF) v0.2 validado pelo
`okf-parser`. O uso segue duas modalidades distintas.

#### Conhecimento autoral

Documentação, RFCs, changelogs, especificações de tipos e conhecimento de
domínio durável serão conceitos Markdown com frontmatter OKF explícito.

- Todo conceito não reservado DEVE declarar `type` não vazio.
- Cada tipo em uso DEVE possuir specification derivada em
  `specs/okf-types/{slug}.md`.
- A ausência de specification será erro normativo desde o início, não warning.
- `index.md` será usado como documento reservado de navegação progressiva.
- Links Markdown serão relações intencionais do grafo, não ornamentação.
- Campos adicionais de frontmatter são permitidos, mas sua semântica deve ser
  declarada na specification do tipo quando houver consumidor.
- `.okfignore`, e não `.gitignore`, define o que fica fora do bundle.

Dados operacionais remotos, tokens, documentos, respostas HTTP e identificadores
reais NÃO são conhecimento autoral e NÃO serão materializados no bundle.
Conhecimento derivado de observação deve registrar proveniência sem copiar o
payload sensível que serviu de fonte.

#### Projeção derivada do runtime

Quando o catálogo crescer, o `suj` gerará em `.generated/okf-mcp/` uma projeção
determinística do servidor FastMCP vivo. Ela poderá representar, conforme houver
consumidor real:

- `MCPTool`;
- `ResponseModel`;
- `RemoteOperation`;
- relações entre tool, contrato e operação remota;
- efeitos e evidências de segurança.

A projeção é descartável e reconstruível; não é fonte de verdade nem dependência
de runtime. O catálogo FastMCP e os modelos Python continuam autoritativos.
Fatos que o FastMCP expõe estruturadamente devem ser lidos dele, preferencialmente
por client in-process. Inferência AST só será aceita para uma relação que o
runtime não exponha, com proveniência explícita e teste de paridade.

O bundle gerado será validado com specifications normativas, materializado em
relações tipadas e submetido apenas a auditorias com pergunta concreta. Não
criaremos taxonomia ou SQL sem consumidor e invariante identificados.

#### Fronteira de adaptação

Fonte externa e OKF autoral não são a mesma coisa. Se CSV, JSON, fixtures ou
outro corpus forem projetados para OKF, um adapter separado deverá declarar:

- a fonte;
- a política de identidade;
- quais campos são observados e quais são derivados;
- a transformação de relações;
- a política de conflito e atualização.

Depois da adaptação, os consumidores operam somente sobre a representação OKF
canônica. O parser, o grafo e as auditorias não aprenderão dialetos de cada
fonte individualmente.

#### Preview antes de escrita

O modelo do `okf-parser` — inspeção e preview disponíveis por default, commit
habilitado separadamente — reforça a política de efeitos deste RFC. Isso não
autoriza escrita judicial, mas estabelece a mesma direção: preparação e efeito
são capabilities diferentes, e annotations nunca substituem autorização.

## Configuração

Configuração não secreta usará `pydantic-settings`, prefixo `SUJ_` e validação
no startup. Defaults devem favorecer offline e ausência de efeitos:

```text
SUJ_NETWORK_ENABLED=false
SUJ_WRITES_ENABLED=false
```

Uma configuração inválida falha cedo e com mensagem acionável. Não haverá
leitura dispersa de `os.environ` nos módulos de domínio ou tools.

## Testes e gates desde o primeiro feature commit

O CI terá um único script local canônico e executará:

1. `ruff check .`;
2. `ruff format --check .`;
3. `ty check src`;
4. `pytest` com cobertura de branch;
5. auditoria de dependências e segurança;
6. teste de construção de duas instâncias MCP independentes;
7. snapshot estrutural do catálogo, sem congelar descrições editoriais;
8. verificação de que todos os modelos públicos geram `outputSchema` útil;
9. teste de que erros não retornam conteúdo com formato de sucesso;
10. teste de ausência de rede em toda a suíte unitária;
11. `okf-parser check . --require-spec 'specs/okf-types/{slug}.md' --normative-spec`;
12. auditorias relacionais OKF específicas, quando existirem.

Os testes de contrato MCP usarão `fastmcp.Client` diretamente sobre a instância
in-process e `pytest-asyncio` com `asyncio_mode = "auto"`. Chamar a função Python
diretamente continua útil para unidade de domínio, mas não substitui atravessar
o schema, a validação, o middleware e o lifecycle reais do servidor.

Mocks devem devolver os mesmos modelos usados em produção. É proibido manter
stub `dict` depois que o contrato real virou Pydantic: esse padrão escondeu no
`pink` uma escrita bem-sucedida seguida de crash no CLI.

Integração remota, quando existir, será marcada e opt-in; nunca fará parte do
pytest default. Nenhum teste de CI usará processo ou credencial real.

## Dependências

Stack inicial aprovada:

- Python 3.12+ e `uv`;
- FastMCP `>=3.4.5,<4` como framework MCP;
- HTTPX para transporte assíncrono;
- Pydantic e `pydantic-settings` para contratos e configuração;
- keyring para custódia local futura;
- Ruff, ty, pytest e pytest-cov para gates locais.
- `okf-parser`, fixado em versão exata, para validação e auditoria de
  conhecimento.

Novas dependências precisam de consumidor imediato. Não serão adicionados
framework de retry, DI, CLI, logging ou result types antes de uma lacuna real.

A linha 4.x estava em beta durante esta revisão de 2026 e muda a base para MCP
Python SDK v2 e protocolo `2026-07-28`. O `suj` não adotará prerelease por
resolução acidental. Migrar para 4.x exigirá RFC curta, catálogo comparado e
testes de contrato passando nos dois lados da atualização.

## Revisão de práticas FastMCP — fontes de 2026

A arquitetura foi confrontada com documentação e releases oficiais disponíveis
em 2026. O resultado é:

| Tema          | RFC antes da revisão | Evidência oficial de 2026                                                                                  | Decisão                                                              |
| ------------- | -------------------- | ---------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------- |
| Defaults      | FastMCP-first        | O framework deriva schemas, structured output e validação de Python idiomático                             | Mantido e elevado a heurística normativa                             |
| Dependências  | Client no lifespan   | `Depends()` exclui dependências runtime do schema público                                                  | Lifespan para recurso compartilhado; DI para dependência por request |
| Lifecycle     | Cleanup previsto     | Lifespan 3.x executa uma vez e recomenda `try/finally`                                                     | Tornado obrigatório                                                  |
| Testes        | Client vivo previsto | A documentação recomenda `Client` in-process + `pytest-asyncio`                                            | Adicionados à stack e aos gates                                      |
| Erros         | Exceções tipadas     | `mask_error_details` protege falhas internas; `ToolError` libera mensagem intencional                      | Mascarar por default e limitar `ToolError` a mensagens seguras       |
| Schemas       | Pydantic direto      | FastMCP gera e dereferencia output schemas por default                                                     | Não customizar nem desligar sem consumidor real                      |
| Timeouts      | HTTPX explícito      | FastMCP 3.x oferece timeout por tool                                                                       | Usar ambas as camadas                                                |
| Middleware    | Só transversal       | Documentação reserva middleware a autenticação, logging e rate limit; transforms a mudanças de componentes | Mantido; middleware não carrega regra específica de uma tool         |
| Autorização   | Política futura      | OAuth/auth checks funcionam em HTTP e são ignorados em stdio                                               | Nunca tratá-los como barreira de escrita em stdio                    |
| Transforms    | Preferir nativos     | FastMCP 3.x fornece namespace, tool transform, visibility e tool search                                    | Built-in antes de transform próprio; nenhum transform preventivo     |
| HTTP security | Allowlist prevista   | Releases 3.4.x corrigiram SSRF, OAuth, Host/Origin e CVE de Starlette                                      | Fixar linha corrigida e exigir configuração explícita no deployment  |
| Major version | Não definido         | FastMCP 4 beta troca SDK e suporta protocolo `2026-07-28`                                                  | Permanecer em 3.x estável até RFC de migração                        |

## Releases e documentação

- SemVer começa em `0.x`; nenhuma estabilidade de protocolo remoto é implícita.
- Cada mudança de comportamento terá changelog junto do bump, nunca depois.
- RFC registra decisão histórica; documento de arquitetura descreve somente o
  estado vigente.
- Código e catálogo MCP são a fonte de verdade; documentação não manterá uma
  lista manual completa de schemas.

## Plano de implementação

### Fase 0 — fundação offline

- aprovar este RFC;
- mover o servidor atual para `mcp/` e introduzir `build_mcp()`;
- criar Settings com rede e escrita desabilitadas;
- definir hierarquia de erros e contratos básicos;
- instalar CI e gates de catálogo;
- validar o bundle OKF e exigir specifications para todos os tipos;
- manter somente `suj_status`.

### Fase 1 — protocolo como fixtures

- modelar respostas observadas com fixtures totalmente sintéticas;
- implementar parsing e mapeamento sem rede;
- documentar proveniência e incertezas de cada campo;
- rejeitar campos desconhecidos somente onde isso represente risco real.

### Fase 2 — leitura remota opt-in

- RFC de autenticação e threat model;
- client HTTP com allowlist, timeouts e redaction;
- primeira tool de leitura;
- smoke test manual separado.

### Fase 3 — escrita

Não começa por extensão natural da fase 2. Exige aprovação explícita da RFC de
escrita descrita no princípio 6.

## Critérios de rejeição imediata em review

Uma mudança deve ser rejeitada se introduzir:

- singleton MCP ou registro por import;
- catálogo ou schema duplicado;
- wrapper sem semântica própria;
- `dict[str, Any]` em resposta pública composta;
- erro representado como resposta bem-sucedida;
- `confirmar: bool` como única barreira para efeito externo;
- retry automático de escrita;
- POST tratado como estado final verificado;
- segredo em Settings, tool, response, fixture ou log;
- rede no import ou no pytest default;
- abstração antes do segundo caso concreto;
- override de default FastMCP sem requisito reproduzível;
- Markdown conceitual sem tipo ou tipo sem specification normativa;
- projeção OKF tratada como fonte de verdade ou dependência de runtime;
- supressão de lint/type check para contornar desenho ruim.

## Questões deliberadamente abertas

- quais hosts e versões da plataforma são realmente interoperáveis;
- como representar proveniência por tribunal sem vazar detalhes de deployment;
- se algum mecanismo oficial de autenticação para aplicações será oferecido;
- qual evidência independente pode verificar cada modalidade de protocolo;
- se escrita deve existir neste projeto, mesmo com todas as barreiras propostas.

Essas questões abertas não bloqueiam a fundação offline. Elas bloqueiam qualquer
promessa de integração real.

## Decisão solicitada

Aprovar a Fase 0 e a Fase 1. Não aprovar, por este RFC, autenticação real,
consulta remota ou protocolo de petições.

## Evidência consultada

- [`pink/docs/architecture.md`](https://github.com/franklinbaldo/pink/blob/main/docs/architecture.md)
- [`pink`: remoção do monólito e mini-framework de tools](https://github.com/franklinbaldo/pink/blob/main/changelog/changes/remove-tools-core-monolith.md)
- [`pink`: composição MCP explícita](https://github.com/franklinbaldo/pink/blob/main/changelog/changes/explicit-mcp-composition.md)
- [`pink`: restauração dos gates de CI](https://github.com/franklinbaldo/pink/blob/main/changelog/changes/restore-ci-gates.md)
- [`todos` RFC 0015: contratos de retorno](https://github.com/franklinbaldo/todos/blob/main/docs/rfc/0015-return-contract.md)
- [`todos` RFC 0019: práticas aprendidas com o Pink](https://github.com/franklinbaldo/todos/blob/main/docs/rfc/0019-adotar-praticas-pink.md)
- [`todos` RFC 0029: reconfirmação pós-escrita](https://github.com/franklinbaldo/todos/blob/main/docs/rfc/0029-reconfirmacao-pos-post-generica.md)
- [`todos` RFC 0035: FastMCP-first](https://github.com/franklinbaldo/todos/blob/main/docs/rfc/0035-nucleo-semantico-de-operacoes.md)
- [`okf-parser`: formato, validação e relações](https://github.com/franklinbaldo/okf-parser)
- [`okf-parser`: fronteira entre bundle estrito e adapters](https://github.com/franklinbaldo/okf-parser/blob/main/docs/architecture.md)
- [FastMCP: server e defaults](https://gofastmcp.com/servers/server)
- [FastMCP: tools, schemas, erros e timeouts](https://gofastmcp.com/servers/tools)
- [FastMCP: dependency injection](https://gofastmcp.com/servers/dependency-injection)
- [FastMCP: lifespans](https://gofastmcp.com/servers/lifespan)
- [FastMCP: middleware](https://gofastmcp.com/servers/middleware)
- [FastMCP: transforms](https://gofastmcp.com/servers/transforms/transforms)
- [FastMCP: autorização](https://gofastmcp.com/servers/authorization)
- [FastMCP: testes](https://gofastmcp.com/patterns/testing)
- [FastMCP: releases de 2026](https://github.com/PrefectHQ/fastmcp/releases)
