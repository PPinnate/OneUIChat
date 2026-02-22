from __future__ import annotations

from app.schemas import FitBreakdown, FitResult
from app.services.registry import ModelRegistry


class FitChecker:
    def __init__(self, registry: ModelRegistry):
        self.registry = registry

    def check(self, model_id: str, variant_id: str, reserve_gb: float) -> FitResult:
        model = self.registry.get_model(model_id)
        variant = self.registry.get_variant(model_id, variant_id)
        weights_gb = float(variant.get("approx_size_gb", 0))

        runtime = model["runtime"]
        if runtime == "llama.cpp":
            runtime_overhead = 2.5
            kv_cache = 1.5
        elif runtime == "diffusers":
            runtime_overhead = 4.0
            kv_cache = 0.0
        else:
            runtime_overhead = 1.5
            kv_cache = 0.0

        unified_memory_gb = float(self.registry.machine_profile["unified_memory_gb"])
        budget = unified_memory_gb - reserve_gb
        estimated_total = weights_gb + runtime_overhead + kv_cache
        fits = estimated_total <= budget

        alternatives: list[str] = []
        if not fits:
            for candidate in model["variants"]:
                candidate_weights = float(candidate.get("approx_size_gb", 0))
                if candidate_weights + runtime_overhead + kv_cache <= budget:
                    alternatives.append(candidate["id"])

        return FitResult(
            status="FITS" if fits else "DOES_NOT_FIT",
            breakdown=FitBreakdown(
                weights_gb=weights_gb,
                runtime_overhead_gb=runtime_overhead,
                kv_cache_gb=kv_cache,
                reserve_gb=reserve_gb,
                budget_gb=budget,
                estimated_total_gb=estimated_total,
            ),
            alternatives=alternatives,
        )
