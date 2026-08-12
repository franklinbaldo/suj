# Copyright (c) 2026 Franklin Baldo
"""Offline characterization of the observed jus.br payload."""

import hashlib
from pathlib import Path

import pytest
from pydantic import ValidationError

from suj.domain.errors import SafeSujError
from suj.jus.models import CapaProcesso, DocumentoProtocolo
from suj.jus.payload import (
    descrever_pdf,
    formatar_cnj,
    montar_payload_protocolo,
    montar_payload_upload,
    somente_digitos,
)

FIXTURE = Path(__file__).parent / "fixtures" / "jus" / "capa_sintetica.json"
SYNTHETIC_CLASS_CODE = 999001
SYNTHETIC_COURT_BODY_CODE = 999002
SYNTHETIC_CASE_VALUE = 12_000_000


@pytest.fixture
def capa() -> CapaProcesso:
    """Load the explicitly fictional, strict observed-response fixture."""
    return CapaProcesso.model_validate_json(FIXTURE.read_text(encoding="utf-8"))


@pytest.fixture
def documento() -> DocumentoProtocolo:
    """Build deterministic synthetic document metadata."""
    return DocumentoProtocolo(
        hash_sha1="f59dcbd3ff4f99ac4e0c641a1caeb2af3fc7acad",
        nome="PETICAO-SINTETICA.pdf",
        descricao="PETICAO-SINTETICA",
        id_tipo_documento=999005,
        nome_tipo_documento="Tipo sintético",
        id_origem_tipo_documento="SYNTHETIC-TYPE-SOURCE",
        tamanho=274049,
    )


def test_cnj_normalizes_in_both_directions() -> None:
    """Punctuation is reversible for the observed 20-digit form."""
    cnj = "0000000-00.2026.8.00.0000"
    assert somente_digitos(cnj) == "00000000020268000000"
    assert formatar_cnj("00000000020268000000") == cnj
    assert formatar_cnj("not-a-cnj") == "not-a-cnj"


def test_payload_derives_known_fields_from_the_detail_response(
    capa: CapaProcesso,
    documento: DocumentoProtocolo,
) -> None:
    """The mapping preserves only fields supported by the synthetic replay."""
    payload = montar_payload_protocolo(
        capa,
        (documento,),
        id_tipo_peticao=999006,
        tipo_peticao="SYNTHETIC",
    )

    assert payload.numero_processo == "0000000-00.2026.8.00.0000"
    assert payload.id_origem_tramitacao == "SYNTHETIC-ORIGIN-1"
    assert payload.codigo_classe_processual == SYNTHETIC_CLASS_CODE
    assert payload.codigo_orgao_julgador_corporativo == SYNTHETIC_COURT_BODY_CODE
    assert payload.valor_causa == SYNTHETIC_CASE_VALUE
    assert isinstance(payload.valor_causa, int)
    assert payload.sigiloso is False
    assert payload.assuntos[0].nome == payload.assuntos[0].descricao


def test_only_lawyers_become_party_representatives(
    capa: CapaProcesso,
    documento: DocumentoProtocolo,
) -> None:
    """The non-lawyer representative is deliberately excluded."""
    payload = montar_payload_protocolo(
        capa,
        (documento,),
        id_tipo_peticao=999006,
        tipo_peticao="SYNTHETIC",
    )

    assert payload.partes[0].modalidade_polo == "AT"
    assert payload.partes[0].advogados == ("REPRESENTANTE SINTÉTICO",)
    assert payload.partes[0].pessoa.numero_documento_principal is None
    assert payload.partes[1].modalidade_polo == "PA"
    assert payload.partes[1].pessoa.numero_documento_principal == "00000000000000"


def test_unknown_pole_fails_instead_of_guessing(
    capa: CapaProcesso,
    documento: DocumentoProtocolo,
) -> None:
    """An unobserved write-side code is a hard domain boundary."""
    unknown_party = capa.tramitacao_atual.partes[0].model_copy(update={"polo": "OUTROS"})
    unknown_proceeding = capa.tramitacao_atual.model_copy(
        update={"partes": (unknown_party, *capa.tramitacao_atual.partes[1:])}
    )
    unknown_capa = capa.model_copy(update={"tramitacao_atual": unknown_proceeding})

    with pytest.raises(SafeSujError, match="não observado"):
        montar_payload_protocolo(
            unknown_capa,
            (documento,),
            id_tipo_peticao=999006,
            tipo_peticao="SYNTHETIC",
        )


def test_missing_document_and_corporate_body_fail_closed(
    capa: CapaProcesso,
    documento: DocumentoProtocolo,
) -> None:
    """Required evidence is never filled with an invented fallback."""
    with pytest.raises(SafeSujError, match="pelo menos um documento"):
        montar_payload_protocolo(capa, (), id_tipo_peticao=1, tipo_peticao="X")

    proceeding = capa.tramitacao_atual.model_copy(update={"distribuicao": ()})
    no_body = capa.model_copy(update={"tramitacao_atual": proceeding})
    with pytest.raises(SafeSujError, match="Órgão julgador"):
        montar_payload_protocolo(
            no_body,
            (documento,),
            id_tipo_peticao=1,
            tipo_peticao="X",
        )


def test_missing_class_fails_closed(
    capa: CapaProcesso,
    documento: DocumentoProtocolo,
) -> None:
    """A class is required by the observed write payload."""
    proceeding = capa.tramitacao_atual.model_copy(update={"classe": ()})
    no_class = capa.model_copy(update={"tramitacao_atual": proceeding})

    with pytest.raises(SafeSujError, match="Classe processual"):
        montar_payload_protocolo(
            no_class,
            (documento,),
            id_tipo_peticao=1,
            tipo_peticao="X",
        )


def test_upload_preserves_observed_string_type_id(documento: DocumentoProtocolo) -> None:
    """Upload and protocol disagree on this field's wire type."""
    upload = montar_payload_upload(documento)
    assert upload.id_tipo_documento == "999005"
    assert isinstance(documento.id_tipo_documento, int)


def test_pdf_description_hashes_in_chunks(tmp_path: Path) -> None:
    """Local description performs no network access and crosses a chunk boundary."""
    content = b"%PDF-1.4 synthetic\n" + b"x" * (1024 * 1024 + 7)
    path = tmp_path / "synthetic.pdf"
    path.write_bytes(content)

    result = descrever_pdf(
        path,
        id_tipo_documento=999005,
        nome_tipo_documento="Tipo sintético",
        id_origem_tipo_documento="SYNTHETIC-TYPE-SOURCE",
    )

    assert result.hash_sha1 == hashlib.sha1(content, usedforsecurity=False).hexdigest()
    assert result.tamanho == len(content)


def test_missing_pdf_fails_before_any_effect(tmp_path: Path) -> None:
    """An absent file is an expected, safe failure."""
    with pytest.raises(SafeSujError, match="Arquivo não encontrado"):
        descrever_pdf(
            tmp_path / "missing.pdf",
            id_tipo_documento=1,
            nome_tipo_documento="Sintético",
            id_origem_tipo_documento="SYNTHETIC",
        )


def test_remote_fixture_rejects_unknown_fields() -> None:
    """Schema drift is visible instead of silently discarded."""
    raw = FIXTURE.read_text(encoding="utf-8")
    with pytest.raises(ValidationError, match="extra_forbidden"):
        CapaProcesso.model_validate_json(raw.replace('"nivelSigilo": 0,', '"unknown": 1,'))
