from pathlib import Path
import json
import pandas as pd



def load_refactoringminer_results(
    class_name: str,
    project_root: Path = Path("."),
) -> pd.DataFrame:
    """
    Load RefactoringMiner results for a given class into a DataFrame.

    Columns:
      iter_no, refactoring_no, refactoring_type, refactoring_description
    """

    base_dir = (
        project_root
        / "analysis"
        / "RefactoringMiner"
        / class_name
    )

    if not base_dir.exists():
        raise FileNotFoundError(f"No RefactoringMiner directory: {base_dir}")

    rows = []

    json_files = sorted(base_dir.glob("iter-*-refactorings.json"))

    if not json_files:
        raise FileNotFoundError(f"No refactoring JSON files found in {base_dir}")

    for json_path in json_files:
        # iter-01-refactorings.json → 1
        iter_no = int(json_path.stem.split("-")[1])

        with open(json_path) as f:
            data = json.load(f)

        commits = data.get("commits", [])
        if not commits:
            continue

        # You are using -bc, so this is normally a single commit
        for commit in commits:
            refactorings = commit.get("refactorings", [])

            for ref_no, ref in enumerate(refactorings, start=1):
                rows.append({
                    "iter_no": iter_no,
                    "refactoring_no": ref_no,
                    "refactoring_type": ref.get("type"),
                    "refactoring_description": ref.get("description"),
                })

    return pd.DataFrame(
        rows,
        columns=[
            "iter_no",
            "refactoring_no",
            "refactoring_type",
            "refactoring_description",
        ],
    )

def export_refactoringminer_csvs(
    class_names: list[str],
    project_root: Path = Path("."),
):
    """
    For each class name, extract RefactoringMiner results
    and save them as a CSV under:

      analysis/RefactoringMiner/<ClassName>/refactorings.csv
    """

    base_out_dir = project_root / "analysis" / "RefactoringMiner"
    base_out_dir.mkdir(parents=True, exist_ok=True)

    for class_name in class_names:
        print(f"\n=== Processing {class_name} ===")

        try:
            df = load_refactoringminer_results(
                class_name=class_name,
                project_root=project_root,
            )
        except FileNotFoundError as e:
            print(f"[SKIP] {e}")
            continue

        class_out_dir = base_out_dir / class_name
        class_out_dir.mkdir(parents=True, exist_ok=True)

        out_csv = class_out_dir / "summary_refactorings.csv"
        df.to_csv(out_csv, index=False)

        print(f"[OK] Saved {len(df)} refactorings → {out_csv}")


TARGET_CLASSES = [
    "Precision",
    "FastMath",
    "MathArrays",
    "Array2DRowRealMatrix",
    "DescriptiveStatistics",
    "SimplexSolver"
]

export_refactoringminer_csvs(TARGET_CLASSES)


