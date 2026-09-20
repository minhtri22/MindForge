"""Fresh-evidence access guard used before M1/M3 execution."""

from __future__ import annotations

from dataclasses import dataclass

from .errors import FreshnessViolation
from .models import ExperimentConfig, RunClass


_FRESH_ALLOWED = {RunClass.CONFIRMATORY, RunClass.RELEASE}


@dataclass(frozen=True)
class FreshnessRegistry:
    seed_ids: frozenset[int]
    dataset_ids: frozenset[str]
    fixture_set_ids: frozenset[str]

    @classmethod
    def from_config(cls, config: ExperimentConfig, fixture_freshness: str | None = None) -> "FreshnessRegistry":
        fresh_seeds = frozenset(config.seed_sets.get("fresh_confirmatory", ()))
        fresh_datasets = frozenset(
            name for name, spec in config.datasets.items() if spec.freshness_class == "fresh_confirmatory"
        )
        fresh_fixtures = frozenset(
            [config.fixture_set] if fixture_freshness == "fresh_confirmatory" else []
        )
        return cls(fresh_seeds, fresh_datasets, fresh_fixtures)

    def assert_access(self, run_class: RunClass, resource_type: str, resource_id: str | int) -> None:
        if run_class in _FRESH_ALLOWED:
            return
        protected = {
            "seed": self.seed_ids,
            "dataset": self.dataset_ids,
            "fixture_set": self.fixture_set_ids,
        }
        if resource_type not in protected:
            raise FreshnessViolation(f"unknown freshness resource type: {resource_type}")
        if resource_id in protected[resource_type]:
            raise FreshnessViolation(
                f"{run_class.value} run cannot access fresh {resource_type} {resource_id!r}"
            )
