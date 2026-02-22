from pathlib import Path

from app.services.fit_checker import FitChecker
from app.services.registry import ModelRegistry


ROOT = Path(__file__).resolve().parents[2]


def test_registry_contains_only_q3_or_smaller_for_chat_code():
    registry = ModelRegistry(ROOT / "registry" / "models.json")
    for model_id in ["chat.qwen3-next-80b-a3b", "code.qwen3-coder-next"]:
        model = registry.get_model(model_id)
        for variant in model["variants"]:
            assert variant["id"].startswith("Q3") or variant["id"].startswith("Q2")


def test_fit_checker_blocks_large_variant_with_high_reserve():
    registry = ModelRegistry(ROOT / "registry" / "models.json")
    checker = FitChecker(registry)
    result = checker.check("chat.qwen3-next-80b-a3b", "Q3_K_L", reserve_gb=15)
    assert result.status == "DOES_NOT_FIT"
    assert "Q2_K" in result.alternatives
