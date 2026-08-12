# suj

> Uma integração não oficial, experimental e potencialmente insegura com o
> jus.br, criada para pesquisa e fins acadêmicos. Não use em processos reais.

`suj` é um servidor MCP para estudar, documentar e experimentar integrações com
serviços expostos pela plataforma `jus.br`.

## Estado do projeto

Este projeto é um experimento independente. Ele não é afiliado, mantido,
homologado ou endossado pelo Conselho Nacional de Justiça, pela Plataforma
Digital do Poder Judiciário, pelo PJe ou por qualquer tribunal.

Não use o `suj` com processos, credenciais, documentos ou dados pessoais reais.
As interfaces observadas podem mudar sem aviso, e operações de escrita podem
produzir efeitos jurídicos irreversíveis.

## Stack

- Python 3.12+
- [uv](https://docs.astral.sh/uv/) para ambiente, dependências e execução
- [FastMCP](https://gofastmcp.com/) para o servidor MCP
- [HTTPX](https://www.python-httpx.org/) para HTTP assíncrono
- [Pydantic](https://docs.pydantic.dev/) e `pydantic-settings` para contratos e configuração
- [keyring](https://pypi.org/project/keyring/) para experimentos locais com credenciais
- Ruff para lint e formatação
- ty para verificação estática de tipos
- pytest e pytest-cov para testes

## Desenvolvimento

```console
uv sync --dev
uv run suj
uv run ruff check .
uv run ruff format --check .
uv run ty check src
uv run pytest
uv run okf-parser check . --require-spec "specs/okf-types/{slug}.md" --normative-spec
```

O servidor inicial publica apenas `suj_status`, sem rede e sem operações de
escrita.

As decisões de fundação, incluindo as lições extraídas dos MCPs `pink` e
`todos`, estão no [RFC 0001](docs/rfc/0001-foundation.md).

## Licença

MIT. Consulte [LICENSE](LICENSE).
