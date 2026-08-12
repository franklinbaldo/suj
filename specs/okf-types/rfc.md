---
type: okf-type-spec
filename: rfc.md
title: "OKF Type: RFC"
description: Registro versionado de uma decisão arquitetural proposta, aceita ou substituída
resource: okf-type:RFC
---

# OKF Type: `RFC`

Uma decisão arquitetural do `suj`, incluindo contexto, alternativas, decisão,
limites e critérios de adoção.

## Campos obrigatórios

| Campo | Tipo | Significado |
| --- | --- | --- |
| `type` | string | Sempre `RFC` |
| `number` | integer | Número estável da decisão |
| `status` | string | `proposed`, `accepted`, `rejected` ou `superseded` |
| `date` | date | Data da proposta |
| `title` | string | Título da decisão |
| `author` | string | Autor responsável |

Um RFC substituído deve apontar por link Markdown para a decisão sucessora.
