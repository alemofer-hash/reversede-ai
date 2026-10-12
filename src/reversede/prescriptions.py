from __future__ import annotations

from typing import Any

import pandas as pd

from .config import ReversedeConfig


def build_prescriptions(
    candidates: pd.DataFrame,
    stress: pd.DataFrame,
    config: ReversedeConfig,
) -> pd.DataFrame:
    stress_by_column = (
        stress.set_index("column").to_dict(orient="index") if not stress.empty else {}
    )
    rows: list[dict[str, Any]] = []
    for candidate in candidates.to_dict(orient="records"):
        column = str(candidate["column"])
        item = stress_by_column.get(column, {})
        evidence: list[str] = []
        recommendations: list[str] = []
        affected: set[str] = set()
        severity = "info"
        confidence = "medium"

        if not candidate["eligible"]:
            evidence.append(str(candidate["reason"]))
            recommendations.append(
                "keep outside the default tabular extractor; review any override explicitly"
            )
            affected.add("all")
            severity = (
                "warning"
                if "leakage" in str(candidate["reason"]) or candidate["probable_id"]
                else "info"
            )
            confidence = "high" if candidate["unique_values"] <= 1 else "medium"
        else:
            kind = str(candidate["kind"])
            null_count = int(item.get("null_count", 0))
            infinite_count = int(item.get("infinite_count", 0))
            if null_count or infinite_count:
                evidence.append(f"missing={null_count}, infinite={infinite_count}")
                recommendations.append(
                    "fit numeric median or categorical mode imputation inside each training fold"
                )
                affected.add("all")
                severity = "warning"
            if kind in {"numeric", "numeric_string"}:
                if kind == "numeric_string":
                    failures = int(item.get("numeric_conversion_failure_count", 0))
                    evidence.append(f"numeric string conversion failures={failures}")
                    recommendations.append(
                        "coerce to numeric inside the pipeline and expose conversion failures"
                    )
                    affected.add("all")
                outlier_fraction = float(item.get("iqr_outlier_fraction", 0.0) or 0.0)
                skewness = float(item.get("skewness", 0.0) or 0.0)
                evidence.append(
                    f"skewness={skewness:.4g}, IQR flagged fraction={outlier_fraction:.4g}"
                )
                if outlier_fraction > config.outlier_fraction_threshold:
                    recommendations.append(
                        "compare RobustScaler with StandardScaler; "
                        "do not drop/winsorize automatically"
                    )
                    affected.update({"linear", "knn"})
                else:
                    recommendations.append(
                        "use StandardScaler for scale-sensitive linear/distance models; "
                        "skip for Random Forest"
                    )
                    affected.update({"linear", "knn"})
                minimum = item.get("minimum")
                if abs(skewness) > 1:
                    if pd.notna(minimum) and float(minimum) >= 0:
                        recommendations.append(
                            "evaluate log1p on training folds only; observed support is nonnegative"
                        )
                    else:
                        recommendations.append(
                            "do not apply log directly; negatives exist, so evaluate "
                            "Yeo-Johnson only if justified"
                        )
                    affected.update({"linear", "knn"})
            elif kind == "categorical":
                levels = int(item.get("unique_values", candidate["unique_values"]))
                rare = int(item.get("rare_level_count", 0))
                evidence.append(f"levels={levels}, rare levels={rare}")
                if levels > config.high_cardinality_levels:
                    recommendations.append(
                        "use bounded one-hot with min_frequency/max_categories or a "
                        "separately cross-fitted encoder"
                    )
                else:
                    recommendations.append(
                        "use OneHotEncoder(handle_unknown='ignore') inside the pipeline"
                    )
                affected.add("all")
            elif kind == "datetime":
                evidence.append(f"suspicious dates={int(item.get('suspicious_date_count', 0))}")
                recommendations.append(
                    "derive calendar parts inside the pipeline and validate temporal semantics"
                )
                affected.add("all")

            collinear = float(item.get("top_abs_spearman", float("nan")))
            if pd.notna(collinear) and collinear >= 0.95:
                partner = item.get("top_collinear_partner")
                evidence.append(f"abs Spearman={collinear:.4f} with {partner}")
                recommendations.append(
                    "inspect redundancy/conditioning; retain unless cross-validation "
                    "supports removal"
                )
                affected.add("linear")
            if bool(candidate["near_constant"]):
                evidence.append(f"dominant fraction={float(candidate['dominant_fraction']):.4f}")
                recommendations.append("compare with/without this near-constant feature")
                affected.add("all")
            if not evidence:
                evidence.append("eligible schema with no threshold-level stress signal")
            if not recommendations:
                recommendations.append("retain for model-conditioned review")
            if candidate["selected"]:
                evidence.append(
                    f"{candidate['association_metric']}={candidate['association_value']!r}, "
                    f"ranking_score={candidate['ranking_score']!r}"
                )

        rows.append(
            {
                "column": column,
                "selected": bool(candidate["selected"]),
                "evidence": "; ".join(evidence),
                "severity": severity,
                "recommendation": "; ".join(recommendations),
                "models_affected": ",".join(sorted(affected)) if affected else "review",
                "confidence": confidence,
                "reason": str(candidate["selection_basis"]),
            }
        )
    return pd.DataFrame(rows)
