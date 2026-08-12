---
type: okf-type-spec
filename: observed-protocol.md
title: "OKF Type: Observed Protocol"
description: Conhecimento experimental derivado de observação não oficial de um protocolo remoto
resource: okf-type:ObservedProtocol
---

# OKF Type: `ObservedProtocol`

Registra comportamento observado de serviço remoto sem promovê-lo a contrato
oficial. Deve separar observação, inferência, incerteza e condições de replay.

## Campos obrigatórios

| Campo               | Tipo   | Significado                                       |
| ------------------- | ------ | ------------------------------------------------- |
| `type`              | string | Sempre `ObservedProtocol`                         |
| `status`            | string | `observed`, `partially-replayed` ou `invalidated` |
| `date`              | date   | Data do registro                                  |
| `title`             | string | Título do protocolo observado                     |
| `source`            | URL    | Fonte rastreável da observação                    |
| `synthetic_fixture` | path   | Fixture sem dados reais usada no replay           |
| `author`            | string | Autor responsável                                 |

O conteúdo não pode incluir token, documento, resposta ou identificador real.
