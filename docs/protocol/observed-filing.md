---
type: ObservedProtocol
status: partially-replayed
date: 2026-08-12
title: Payload de peticionamento observado no jus.br
source: https://github.com/franklinbaldo/pink/pull/452
synthetic_fixture: tests/fixtures/jus/capa_sintetica.json
author: Franklin Baldo
---

# Payload de peticionamento observado

Este registro preserva o conhecimento puro extraído da PR `pink#452`. Não é
documentação oficial do `jus.br`, não prova interoperabilidade entre tribunais e
não autoriza chamadas remotas.

## Observado e reproduzido offline

- a consulta detalhada fornece `idOrigem`, grau, classe, órgão julgador
  corporativo, assuntos, partes, tribunal e permissão para peticionar;
- o protocolo usa o órgão corporativo, não eventual órgão local;
- polos `ATIVO` e `PASSIVO` foram mapeados respectivamente para `AT` e `PA`;
- somente representantes marcados `ADVOGADO` entram na lista observada;
- o valor numérico recebido como ponto flutuante foi emitido como inteiro;
- o tipo de documento apareceu como inteiro no protocolo e string no handshake
  de upload;
- o PDF é descrito por nome, tamanho, MIME type e SHA-1 local.

Essas invariantes vivem em `suj.jus.models`, `suj.jus.payload` e na fixture
sintética indicada no frontmatter. Os DTOs rejeitam campos extras para tornar
drift visível durante esta fase de caracterização.

## Inferido de uma única amostra — não usar como default

- `idTipoPeticao=50`;
- `tipo=A`;
- `idOrigemTipoDocumento=2`;
- códigos de tipo de documento e sua disponibilidade por tribunal.

Por isso esses valores permanecem argumentos explícitos no domínio offline.
Nenhum deles está publicado como tool.

## Desconhecido

- código write-side para `OUTROS_PARTICIPANTES`;
- estabilidade dos endpoints e dos campos;
- semântica de idempotência e replay;
- validade e allowlist de hosts para URLs pré-assinadas;
- evidência suficiente para distinguir submissão de protocolo verificado.

Entradas desconhecidas que afetem o destino do protocolo falham sem inferência.
As questões de rede e escrita permanecem bloqueadas pelas issues do épico #16.
