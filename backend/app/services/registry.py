from __future__ import annotations

import json
from pathlib import Path
from typing import Any


class ModelRegistry:
    def __init__(self, registry_path: Path):
        self.registry_path = registry_path
        self._data = self._load()

    def _load(self) -> dict[str, Any]:
        with self.registry_path.open("r", encoding="utf-8") as f:
            return json.load(f)

    @property
    def machine_profile(self) -> dict[str, Any]:
        return self._data["machine_profile"]

    def all_models(self) -> list[dict[str, Any]]:
        return self._data["models"]

    def get_model(self, model_id: str) -> dict[str, Any]:
        model = next((m for m in self._data["models"] if m["id"] == model_id), None)
        if not model:
            raise ValueError(f"Unknown model_id: {model_id}")
        return model

    def get_variant(self, model_id: str, variant_id: str) -> dict[str, Any]:
        model = self.get_model(model_id)
        variant = next((v for v in model["variants"] if v["id"] == variant_id), None)
        if not variant:
            raise ValueError(f"Unknown variant_id '{variant_id}' for model '{model_id}'")
        merged = dict(variant)
        merged["repo_id"] = variant.get("repo_id_override") or model["repo_id"]
        merged["runtime"] = model["runtime"]
        return merged
