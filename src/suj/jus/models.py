# Copyright (c) 2026 Franklin Baldo
"""Strict DTOs for the observed read and write payloads."""

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class ObservedModel(BaseModel):
    """Base for synthetic representations of observed remote data."""

    model_config = ConfigDict(alias_generator=None, extra="forbid", frozen=True)


class Tribunal(ObservedModel):
    """Court identity required by the observed payload."""

    sigla: str
    jtr: str


class Grau(ObservedModel):
    """Proceeding level reported by the detail endpoint."""

    sigla: str
    numero: int


class Classe(ObservedModel):
    """Procedural class."""

    codigo: int
    descricao: str


class OrgaoJulgador(ObservedModel):
    """Corporate adjudicating body recognized by the national layer."""

    id: int
    nome: str


class Distribuicao(ObservedModel):
    """Distribution entry containing the corporate body."""

    orgao_julgador: tuple[OrgaoJulgador, ...] = Field(alias="orgaoJulgador")


class Assunto(ObservedModel):
    """Subject attached to the current proceeding."""

    codigo: int
    descricao: str


class DocumentoIdentificador(ObservedModel):
    """A party's primary identifier in the observed response."""

    numero: str
    tipo: Literal["CPF", "CNPJ"]


class Representante(ObservedModel):
    """A party representative."""

    tipo_representacao: str = Field(alias="tipoRepresentacao")
    nome: str
    cadastro_receita_federal: tuple[DocumentoIdentificador, ...] = Field(
        default=(), alias="cadastroReceitaFederal"
    )


class Parte(ObservedModel):
    """A party whose write-side pole mapping is partially observed."""

    polo: str
    nome: str
    documentos_principais: tuple[DocumentoIdentificador, ...] = Field(
        default=(), alias="documentosPrincipais"
    )
    representantes: tuple[Representante, ...] = ()


class TramitacaoAtual(ObservedModel):
    """Fields known to be required for the observed filing payload."""

    id_origem: str = Field(alias="idOrigem")
    distribuido_em: datetime = Field(alias="dataHoraAjuizamento")
    grau: Grau
    valor_causa: int | float = Field(alias="valorAcao")
    classe: tuple[Classe, ...]
    distribuicao: tuple[Distribuicao, ...]
    assunto: tuple[Assunto, ...]
    partes: tuple[Parte, ...]
    tribunal: Tribunal
    permite_peticionar: bool = Field(alias="permitePeticionar")
    id_fonte_dados_codex: int = Field(alias="idFonteDadosCodex")


class CapaProcesso(ObservedModel):
    """Minimal strict projection of the observed process detail response."""

    nivel_sigilo: int = Field(alias="nivelSigilo")
    sigla_tribunal: str = Field(alias="siglaTribunal")
    numero_processo: str = Field(alias="numeroProcesso")
    tramitacao_atual: TramitacaoAtual = Field(alias="tramitacaoAtual")


class DocumentoProtocolo(ObservedModel):
    """Immutable local description of one document prepared for upload."""

    hash_sha1: str
    nome: str
    descricao: str
    id_tipo_documento: int
    nome_tipo_documento: str
    id_origem_tipo_documento: str
    mime_type: Literal["application/pdf"] = "application/pdf"
    tamanho: int
    principal: bool = True
    sigiloso: bool = False


class PessoaProtocolo(ObservedModel):
    """Observed write-side person projection."""

    nome: str
    numero_documento_principal: str | None
    modalidade_documento_identificador: Literal["CPF", "CNPJ"] | None


class ParteProtocolo(ObservedModel):
    """Observed write-side party projection."""

    modalidade_polo: Literal["AT", "PA"]
    pessoa: PessoaProtocolo
    advogados: tuple[str, ...]


class AssuntoProtocolo(ObservedModel):
    """Observed write-side subject projection."""

    codigo: int
    nome: str
    descricao: str


class PeticaoDocumento(ObservedModel):
    """Document metadata embedded in the filing payload."""

    hash_sha1: str
    nome: str
    id_tipo_documento: int
    id_origem_tipo_documento: str
    tamanho: int
    mime_type: Literal["application/pdf"]


class PayloadProtocolo(ObservedModel):
    """Canonical typed representation of the single observed filing shape."""

    numero_processo: str
    distribuido_em: datetime
    codigo_classe_processual: int
    sigla_tribunal: str
    jtr_tribunal: str
    id_origem_tramitacao: str
    sigla_grau: str
    numero_grau: int
    codigo_orgao_julgador_corporativo: int
    nome_orgao_julgador_corporativo: str
    valor_causa: int
    sigiloso: bool
    permite_peticionar: bool
    id_fonte_dados_codex: int
    assuntos: tuple[AssuntoProtocolo, ...]
    partes: tuple[ParteProtocolo, ...]
    documentos: tuple[PeticaoDocumento, ...]
    id_tipo_peticao: int
    tipo_peticao: str


class PayloadUpload(ObservedModel):
    """Typed upload-handshake body; its string type id is intentional."""

    nome: str
    hash_sha1: str
    tamanho: int
    id_tipo_documento: str
    mime_type: Literal["application/pdf"]
