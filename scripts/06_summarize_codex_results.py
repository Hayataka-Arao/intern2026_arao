from pathlib import Path
import json
import pandas as pd
import re


def summarize_codex_experiments(
    project_root: Path,
    class_names: list[str],
) -> pd.DataFrame:
    """
    Summarize Codex refactoring experiments per class.

    Columns:
      - class_name
      - num_iterations
      - num_tests_run
      - failure_reason
    """

    rows = []

    for class_name in class_names:
        repos_dir = project_root / "repos" / class_name
        artifacts_dir = project_root / "analysis" / "codex-artifacts" / class_name

        # -------------------------
        # Count iterations
        # -------------------------
        iter_dirs = []
        if repos_dir.exists():
            iter_dirs = sorted(
                d for d in repos_dir.iterdir()
                if d.is_dir() and d.name.startswith("iter-")
            )

        num_iterations = len(iter_dirs)

        # -------------------------
        # Load artifacts
        # -------------------------
        artifacts = []
        if artifacts_dir.exists():
            artifacts = sorted(artifacts_dir.glob("iter-*-codex.json"))

        first_meta = None
        last_meta = None

        if artifacts:
            with open(artifacts[0]) as f:
                first_meta = json.load(f)
            with open(artifacts[-1]) as f:
                last_meta = json.load(f)

        # -------------------------
        # Extract number of tests run (FIRST iteration)
        # -------------------------
        num_tests_run = None

        if first_meta:
            tests = first_meta.get("tests", {})
            stdout = tests.get("stdout", "")

            # Maven canonical summary line
            m = re.search(
                r"Tests run:\s*(\d+),\s*Failures:\s*\d+,\s*Errors:\s*\d+,\s*Skipped:\s*\d+",
                stdout,
            )

            if m:
                num_tests_run = int(m.group(1))
            else:
                num_tests_run = 0

        # -------------------------
        # Extract failure reason (LAST iteration)
        # -------------------------
        failure_reason = None

        if last_meta:
            tests = last_meta.get("tests", {})
            stdout = tests.get("stdout", "")

            # 1. Test failures
            if re.search(r"Tests run:\s*\d+,\s*Failures:\s*[1-9]", stdout):
                failure_reason = "test failures"

            # 2. Compilation errors
            elif "COMPILATION ERROR" in stdout:
                failure_reason = "compilation error"

            # 3. Maven build failure (non-test)
            elif "BUILD FAILURE" in stdout:
                failure_reason = "maven build failure"

            # 4. Codex explicitly stopped
            elif last_meta.get("failure") == "no_changes":
                failure_reason = "no changes needed"

            elif last_meta.get("failure"):
                failure_reason = last_meta["failure"]

            # 5. Otherwise, tests passed
            else:
                failure_reason = None


            rows.append({
                "class_name": class_name,
                "num_iterations": num_iterations,
                "num_tests_run": num_tests_run,
                "failure_reason": failure_reason,
            })

    return pd.DataFrame(rows)


PROJECT_ROOT = Path(".")

TARGET_CLASSES = [
    "Precision",
    "FastMath",
    "MathArrays",
    "Array2DRowRealMatrix",
    "DescriptiveStatistics",
    "SimplexSolver"
]

summary_df = summarize_codex_experiments(
    project_root=PROJECT_ROOT,
    class_names=TARGET_CLASSES,
)

summary_df.to_csv(
    PROJECT_ROOT / "analysis" / "experiment_summary.csv",
    index=False,
)

print(summary_df)
