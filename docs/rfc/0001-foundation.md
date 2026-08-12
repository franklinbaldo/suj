# RFC 0001 — Fundação arquitetural do `suj`

- Status: proposta
- Data: 2026-08-12
- Autor: Franklin Baldo
- Escopo: arquitetura inicial, contratos, segurança e processo de evolução

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
10. teste de ausência de rede em toda a suíte unitária.

Mocks devem devolver os mesmos modelos usados em produção. É proibido manter
stub `dict` depois que o contrato real virou Pydantic: esse padrão escondeu no
`pink` uma escrita bem-sucedida seguida de crash no CLI.

Integração remota, quando existir, será marcada e opt-in; nunca fará parte do
pytest default. Nenhum teste de CI usará processo ou credencial real.

## Dependências

Stack inicial aprovada:

- Python 3.12+ e `uv`;
- FastMCP como framework MCP;
- HTTPX para transporte assíncrono;
- Pydantic e `pydantic-settings` para contratos e configuração;
- keyring para custódia local futura;
- Ruff, ty, pytest e pytest-cov para gates locais.

Novas dependências precisam de consumidor imediato. Não serão adicionados
framework de retry, DI, CLI, logging ou result types antes de uma lacuna real.

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
