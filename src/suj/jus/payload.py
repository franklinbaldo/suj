# Copyright (c) 2026 Franklin Baldo
"""Pure transformations derived from one synthetic replay of an observed flow."""

import hashlib
from pathlib import Path
from typing import Literal

from suj.domain.errors import SafeSujError
from suj.jus.models import (
    AssuntoProtocolo,
    CapaProcesso,
    DocumentoProtocolo,
    Parte,
    ParteProtocolo,
    PayloadProtocolo,
    PayloadUpload,
    PessoaProtocolo,
    PeticaoDocumento,
)

CNJ_LENGTH = 20
POLOS_OBSERVADOS: dict[str, Literal["AT", "PA"]] = {"ATIVO": "AT", "PASSIVO": "PA"}
ARQUIVO_AUSENTE = "Arquivo não encontrado."
POLO_DESCONHECIDO = "Polo processual não observado; recusado sem inferência."
DOCUMENTO_AUSENTE = "O protocolo exige pelo menos um documento."
CLASSE_AUSENTE = "Classe processual ausente na resposta observada."
ORGAO_AUSENTE = "Órgão julgador corporativo ausente na resposta observada."


def somente_digitos(numero: str) -> str:
    """Remove CNJ punctuation without claiming that the number is valid."""
    return "".join(character for character in numero if character.isdigit())


def formatar_cnj(numero: str) -> str:
    """Format a 20-digit CNJ number, preserving unknown input for validation."""
    digits = somente_digitos(numero)
    if len(digits) != CNJ_LENGTH:
        return numero
    return f"{digits[:7]}-{digits[7:9]}.{digits[9:13]}.{digits[13]}.{digits[14:16]}.{digits[16:]}"


def sha1_do_arquivo(path: Path) -> str:
    """Calculate the digest required by the observed protocol in bounded chunks."""
    digest = hashlib.sha1(usedforsecurity=False)
    with path.open("rb") as stream:
        while chunk := stream.read(1024 * 1024):
            digest.update(chunk)
    return digest.hexdigest()


def descrever_pdf(
    path: Path,
    *,
    id_tipo_documento: int,
    nome_tipo_documento: str,
    id_origem_tipo_documento: str,
) -> DocumentoProtocolo:
    """Describe a local synthetic PDF without performing network access."""
    if not path.is_file():
        raise SafeSujError(ARQUIVO_AUSENTE)
    return DocumentoProtocolo(
        hash_sha1=sha1_do_arquivo(path),
        nome=path.name,
        descricao=path.stem,
        id_tipo_documento=id_tipo_documento,
        nome_tipo_documento=nome_tipo_documento,
        id_origem_tipo_documento=id_origem_tipo_documento,
        tamanho=path.stat().st_size,
    )


def _mapear_parte(parte: Parte) -> ParteProtocolo:
    modalidade = POLOS_OBSERVADOS.get(parte.polo)
    if modalidade is None:
        raise SafeSujError(POLO_DESCONHECIDO)
    documento = parte.documentos_principais[0] if parte.documentos_principais else None
    return ParteProtocolo(
        modalidade_polo=modalidade,
        pessoa=PessoaProtocolo(
            nome=parte.nome,
            numero_documento_principal=documento.numero if documento else None,
            modalidade_documento_identificador=documento.tipo if documento else None,
        ),
        advogados=tuple(
            representante.nome
            for representante in parte.representantes
            if representante.tipo_representacao == "ADVOGADO"
        ),
    )


def montar_payload_protocolo(
    capa: CapaProcesso,
    documentos: tuple[DocumentoProtocolo, ...],
    *,
    id_tipo_peticao: int,
    tipo_peticao: str,
) -> PayloadProtocolo:
    """Build the typed form of the single observed filing request."""
    if not documentos:
        raise SafeSujError(DOCUMENTO_AUSENTE)
    tramitacao = capa.tramitacao_atual
    if not tramitacao.classe:
        raise SafeSujError(CLASSE_AUSENTE)
    orgaos = tuple(
        orgao for distribuicao in tramitacao.distribuicao for orgao in distribuicao.orgao_julgador
    )
    if not orgaos:
        raise SafeSujError(ORGAO_AUSENTE)
    classe = tramitacao.classe[0]
    orgao = orgaos[0]
    return PayloadProtocolo(
        numero_processo=formatar_cnj(capa.numero_processo),
        distribuido_em=tramitacao.distribuido_em,
        codigo_classe_processual=classe.codigo,
        sigla_tribunal=capa.sigla_tribunal,
        jtr_tribunal=tramitacao.tribunal.jtr,
        id_origem_tramitacao=tramitacao.id_origem,
        sigla_grau=tramitacao.grau.sigla,
        numero_grau=tramitacao.grau.numero,
        codigo_orgao_julgador_corporativo=orgao.id,
        nome_orgao_julgador_corporativo=orgao.nome,
        valor_causa=int(tramitacao.valor_causa),
        sigiloso=bool(capa.nivel_sigilo),
        permite_peticionar=tramitacao.permite_peticionar,
        id_fonte_dados_codex=tramitacao.id_fonte_dados_codex,
        assuntos=tuple(
            AssuntoProtocolo(codigo=item.codigo, nome=item.descricao, descricao=item.descricao)
            for item in tramitacao.assunto
        ),
        partes=tuple(_mapear_parte(parte) for parte in tramitacao.partes),
        documentos=tuple(
            PeticaoDocumento(
                hash_sha1=documento.hash_sha1,
                nome=documento.nome,
                id_tipo_documento=documento.id_tipo_documento,
                id_origem_tipo_documento=documento.id_origem_tipo_documento,
                tamanho=documento.tamanho,
                mime_type=documento.mime_type,
            )
            for documento in documentos
        ),
        id_tipo_peticao=id_tipo_peticao,
        tipo_peticao=tipo_peticao,
    )


def montar_payload_upload(documento: DocumentoProtocolo) -> PayloadUpload:
    """Preserve the upstream inconsistency that serializes the type id as text."""
    return PayloadUpload(
        nome=documento.nome,
        hash_sha1=documento.hash_sha1,
        tamanho=documento.tamanho,
        id_tipo_documento=str(documento.id_tipo_documento),
        mime_type=documento.mime_type,
    )
