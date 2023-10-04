import logging
import os
import secrets
from typing import Any

from pydantic import AnyHttpUrl, BaseModel, EmailStr, HttpUrl, PostgresDsn, field_validator
from pydantic_core.core_schema import ValidationInfo
from pydantic_settings import BaseSettings, SettingsConfigDict

logger = logging.getLogger(__name__)


class Settings(BaseSettings):
    """Configuration of dotty web server."""

    #: Enable loading variables from ``.env`` files.
    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", case_sensitive=True
    )

    #: Path to the directory with the cdot ``.json.gz`` files.
    DATA_DIR: str = "/data"

    #: Whether seqrepo is available for the reference, allows normalization
    #: of reference-level variants.
    HAVE_SEQREPO: bool = True


settings = Settings(_env_file=".env", _env_file_encoding="utf-8")  # type: ignore[call-arg]
