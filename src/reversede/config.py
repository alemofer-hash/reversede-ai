from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class ReversedeConfig:
    """Configuration for auditable heuristics; no learned values are stored here."""

    max_features: int = 20
    max_categorical_levels: int = 50
    high_cardinality_levels: int = 25
    near_constant_threshold: float = 0.995
    id_unique_fraction: float = 0.98
    target_confidence_threshold: float = 0.88
    target_margin: float = 0.08
    rare_category_fraction: float = 0.01
    outlier_fraction_threshold: float = 0.05
    include_columns: tuple[str, ...] = field(default_factory=tuple)
    exclude_columns: tuple[str, ...] = field(default_factory=tuple)

    def validate(self) -> None:
        if self.max_features < 1:
            raise ValueError("max_features must be at least 1")
        if self.max_categorical_levels < 2 or self.high_cardinality_levels < 2:
            raise ValueError("categorical level limits must be at least 2")
        for name, value in {
            "near_constant_threshold": self.near_constant_threshold,
            "id_unique_fraction": self.id_unique_fraction,
            "target_confidence_threshold": self.target_confidence_threshold,
            "target_margin": self.target_margin,
            "rare_category_fraction": self.rare_category_fraction,
            "outlier_fraction_threshold": self.outlier_fraction_threshold,
        }.items():
            if not 0 <= value <= 1:
                raise ValueError(f"{name} must be between 0 and 1")
