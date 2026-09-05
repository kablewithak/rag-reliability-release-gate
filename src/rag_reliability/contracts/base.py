"""Shared contract primitives."""

from typing import Annotated

from pydantic import BaseModel, ConfigDict, StringConstraints

NonEmptyStr = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1)]
Sha256 = Annotated[str, StringConstraints(pattern=r"^[0-9a-f]{64}$")]
GitCommitSha = Annotated[str, StringConstraints(pattern=r"^[0-9a-f]{40,64}$")]


class ContractModel(BaseModel):
    """Strict immutable base model for deterministic boundary contracts."""

    model_config = ConfigDict(
        extra="forbid",
        frozen=True,
        str_strip_whitespace=True,
        validate_default=True,
    )
