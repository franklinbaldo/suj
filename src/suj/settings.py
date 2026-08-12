# Copyright (c) 2026 Franklin Baldo
"""Non-secret process configuration."""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Fail-closed configuration; secrets are intentionally absent."""

    model_config = SettingsConfigDict(
        env_prefix="SUJ_",
        extra="forbid",
        frozen=True,
    )

    network_enabled: bool = False
    writes_enabled: bool = False
