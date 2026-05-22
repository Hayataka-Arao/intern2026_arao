import subprocess
from pathlib import Path


class RefactoringMinerError(RuntimeError):
    pass


def run_refactoring_miner(
    repo_path: Path,
    output_json: Path,
    rm_jar: Path | None = None,
    before_ref: str = "HEAD~1",
    after_ref: str = "HEAD",
):
    """
    Run RefactoringMiner between two commits in a git repo.

    Parameters
    ----------
    repo_path : Path
        Path to the git repository (e.g. repos/iter-01-commons-math)
    output_json : Path
        Where to write the JSON output
    rm_jar : Path, optional
        Path to RM-fat.jar (defaults to tools/RefactoringMiner/build/libs/RM-fat.jar)
    before_ref : str
        Git ref for baseline (default: HEAD~1)
    after_ref : str
        Git ref for variant (default: HEAD)
    """

    if rm_jar is None:
        rm_jar = Path("tools/RefactoringMiner/build/libs/RM-fat.jar")

    # ---- Preconditions -----------------------------------------------------

    if not rm_jar.exists():
        raise RefactoringMinerError(f"RefactoringMiner jar not found: {rm_jar}")

    if not repo_path.exists():
        raise RefactoringMinerError(f"Repo path does not exist: {repo_path}")

    if not (repo_path / ".git").exists():
        raise RefactoringMinerError(f"Not a git repository: {repo_path}")

    output_json.parent.mkdir(parents=True, exist_ok=True)

    # ---- Command -----------------------------------------------------------

    cmd = [
        "java",
        "-jar",
        str(rm_jar),
        "-bc",
        str(repo_path),
        before_ref,
        after_ref,
        "-json",
        str(output_json),
    ]

    print("[RefactoringMiner] Running:")
    print(" ", " ".join(cmd))

    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
    )

    # ---- Error handling ----------------------------------------------------

    if result.returncode != 0:
        print("----- STDOUT -----")
        print(result.stdout)
        print("----- STDERR -----")
        print(result.stderr)
        raise RefactoringMinerError("RefactoringMiner failed")

    if not output_json.exists():
        raise RefactoringMinerError("RefactoringMiner did not produce output JSON")

    print(f"[RefactoringMiner] Results written to {output_json}")

    return output_json

def class_dir_name(target_class: str) -> str:
    """
    Convert a Java source path to a stable directory name.
    Example:
      src/main/java/org/apache/commons/math3/util/Precision.java
      -> Precision
    """
    return Path(target_class).stem

PROJECT_ROOT = Path(".")
BASELINE_REPO = "baseline-commons-math"

TARGET_CLASSES = [
    "src/main/java/org/apache/commons/math3/util/Precision.java",
    "src/main/java/org/apache/commons/math3/linear/Array2DRowRealMatrix.java",
    "src/main/java/org/apache/commons/math3/stat/descriptive/DescriptiveStatistics.java",
    "src/main/java/org/apache/commons/math3/util/MathArrays.java",
    "src/main/java/org/apache/commons/math3/optim/linear/SimplexSolver.java",
    "src/main/java/org/apache/commons/math3/util/FastMath.java"
]


if __name__ == "__main__":
    for target_class in TARGET_CLASSES:
        class_name = class_dir_name(target_class)

        repos_class_dir = PROJECT_ROOT / "repos" / class_name
        analysis_class_dir = PROJECT_ROOT / "analysis" / "refactoringminer" / class_name

        if not repos_class_dir.exists():
            print(f"[Skip] No repo directory for {target_class}")
            continue

        # Discover iterations dynamically
        iter_dirs = sorted(
            [
                p for p in repos_class_dir.iterdir()
                if p.is_dir() and p.name.startswith("iter-") and p.name.endswith("-commons-math")
            ],
            key=lambda p: int(p.name.split("-")[1]),
        )

        if not iter_dirs:
            print(f"[Skip] No iterations found for {target_class}")
            continue

        print(f"\n=== Analyzing refactorings for {target_class} ===")

        for repo_path in iter_dirs:
            iter_num = int(repo_path.name.split("-")[1])

            print(f"\n=== Iteration {iter_num} of {target_class} ===")

            output_json = (
                analysis_class_dir /
                f"iter-{iter_num:02d}-refactorings.json"
            )

            run_refactoring_miner(
                repo_path=repo_path,
                output_json=output_json,
            )
