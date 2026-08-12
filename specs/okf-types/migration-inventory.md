---
type: okf-type-spec
filename: migration-inventory.md
title: "OKF Type: Migration Inventory"
description: Inventário rastreável para migração de conhecimento e código entre repositórios
resource: okf-type:MigrationInventory
---

# OKF Type: `MigrationInventory`

Registra a avaliação de uma fonte externa antes de qualquer migração. O inventário
separa o que pode ser portado, o que exige reescrita e o que deve ser descartado,
sempre com evidência verificável e destino explícito.

## Campos obrigatórios

| Campo    | Tipo   | Significado                                      |
| -------- | ------ | ------------------------------------------------ |
| `type`   | string | Sempre `MigrationInventory`                      |
| `status` | string | `draft`, `accepted`, `in-progress` ou `complete` |
| `date`   | date   | Data do inventário                               |
| `title`  | string | Título do inventário                             |
| `source` | URL    | Fonte imutável ou revisão identificável          |
| `target` | string | Repositório ou componente de destino             |
| `author` | string | Autor responsável                                |

Cada item deve indicar classificação, racional, evidência na fonte e trabalho de
destino. O inventário não autoriza, por si só, efeitos externos nem a cópia de
segredos ou dados pessoais.
