from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, Field


class VariantRef(BaseModel):
    model_id: str
    variant_id: str


class SizeRequest(VariantRef):
    pass


class DownloadRequest(VariantRef):
    token: str | None = None


class ExploreRequest(VariantRef):
    token: str | None = None


class TokenRequest(BaseModel):
    token: str = Field(min_length=10)


class SettingsPatch(BaseModel):
    model_cache_dir: str | None = None
    reserve_gb: float | None = Field(default=None, ge=2, le=20)


class ChatRequest(BaseModel):
    prompt: str = Field(min_length=1)
    system_prompt: str = ""


class FitBreakdown(BaseModel):
    weights_gb: float
    runtime_overhead_gb: float
    kv_cache_gb: float
    reserve_gb: float
    budget_gb: float
    estimated_total_gb: float


class FitResult(BaseModel):
    status: Literal["FITS", "DOES_NOT_FIT"]
    breakdown: FitBreakdown
    alternatives: list[str] = []


class DownloadSizeResponse(BaseModel):
    repo_id: str
    total_bytes: int
    total_gb: float
    files: list[dict[str, Any]]


class StatusResponse(BaseModel):
    machine: str
    unified_memory_gb: int
    reserve_gb: float
    workers: dict[str, Any]
