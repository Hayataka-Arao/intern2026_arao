import pandas as pd
import re
from pathlib import Path


def load_designite_smells_for_class(
    class_name: str,
    project_root: Path = Path("."),
) -> pd.DataFrame:

    base_dir = project_root / "analysis" / "designite" / class_name
    rows = []

    if not base_dir.exists():
        raise FileNotFoundError(f"Missing Designite dir: {base_dir}")

    # ---------------------------
    # Baseline (iter_no = 0)
    # ---------------------------
    baseline_csv = base_dir / "baseline" / "designCodeSmells.csv"
    if baseline_csv.exists():
        df = pd.read_csv(baseline_csv)
        df.columns = df.columns.str.strip()
        df = df[df["Type Name"] == class_name]

        for _, r in df.iterrows():
            rows.append({
                "iter_no": 0,
                "project_name": r["Project Name"],
                "package_name": r["Package Name"],
                "type_name": r["Type Name"],
                "code_smell": r["Code Smell"],
            })

    # ---------------------------
    # Iterations (iter-XX / iter_XX)
    # ---------------------------
    for iter_dir in sorted(d for d in base_dir.iterdir() if d.is_dir()):
        m = re.search(r"iter[-_](\d+)", iter_dir.name)
        if not m:
            continue

        iter_no = int(m.group(1))
        csv_path = iter_dir / "designCodeSmells.csv"

        if not csv_path.exists():
            continue

        df = pd.read_csv(csv_path)
        df.columns = df.columns.str.strip()
        df = df[df["Type Name"] == class_name]

        for _, r in df.iterrows():
            rows.append({
                "iter_no": iter_no,
                "project_name": r["Project Name"],
                "package_name": r["Package Name"],
                "type_name": r["Type Name"],
                "code_smell": r["Code Smell"],
            })

    return pd.DataFrame(
        rows,
        columns=[
            "iter_no",
            "project_name",
            "package_name",
            "type_name",
            "code_smell",
        ],
    )

def load_designite_type_metrics_for_class(
    class_name: str,
    project_root: Path = Path("."),
) -> pd.DataFrame:

    base_dir = project_root / "analysis" / "designite" / class_name
    rows = []

    if not base_dir.exists():
        raise FileNotFoundError(f"Designite directory not found: {base_dir}")

    # ---------------------------
    # Baseline (iter_no = 0)
    # ---------------------------
    baseline_metrics = base_dir / "baseline" / "typeMetrics.csv"
    if baseline_metrics.exists():
        df = pd.read_csv(baseline_metrics)
        df.columns = df.columns.str.strip()
        df = df[df["Type Name"] == class_name]

        if not df.empty:
            row = df.iloc[0].to_dict()
            row["iter_no"] = 0
            rows.append(row)

    # ---------------------------
    # Iterations
    # ---------------------------
    for iter_dir in sorted(d for d in base_dir.iterdir() if d.is_dir()):
        m = re.search(r"iter[-_](\d+)", iter_dir.name)
        if not m:
            continue

        iter_no = int(m.group(1))
        metrics_path = iter_dir / "typeMetrics.csv"
        if not metrics_path.exists():
            continue

        df = pd.read_csv(metrics_path)
        df.columns = df.columns.str.strip()

        if "Type Name" not in df.columns:
            continue

        df = df[df["Type Name"] == class_name]
        if df.empty:
            continue

        row = df.iloc[0].to_dict()
        row["iter_no"] = iter_no
        rows.append(row)

    if not rows:
        return pd.DataFrame()

    metrics_df = (
        pd.DataFrame(rows)
        .sort_values("iter_no")
        .reset_index(drop=True)
    )

    cols = ["iter_no"] + [c for c in metrics_df.columns if c != "iter_no"]
    return metrics_df[cols]


TARGET_CLASSES = [
    "Precision",
    "FastMath",
    "MathArrays",
    "Array2DRowRealMatrix",
    "DescriptiveStatistics",
    "SimplexSolver"
]

analysis_dir = Path(".") / "analysis" / "designite"

for class_name in TARGET_CLASSES:
    df = load_designite_smells_for_class(class_name)    
    out_dir = analysis_dir / class_name
    df.to_csv(out_dir / "designite_smells_long.csv", index=False)
    print(f"[OK] Extracted design smells → {class_name}")

    df = load_designite_type_metrics_for_class(class_name)
    out_dir = analysis_dir / class_name
    df.to_csv(out_dir / "designite_type_metrics.csv", index=False)
    print(f"[OK] Extracted type Metrics → {class_name}")

    
