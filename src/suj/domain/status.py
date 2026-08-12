# Copyright (c) 2026 Franklin Baldo
"""Public status contract."""

from typing import Literal

from pydantic import BaseModel, ConfigDict


class SujStatus(BaseModel):
    """The experimental server's current safety posture."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    status: Literal["experimental"] = "experimental"
    disclaimer: str
    network_enabled: bool
    writes_enabled: bool
