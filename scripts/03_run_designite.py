import subprocess
from pathlib import Path
from typing import Dict


class DesigniteFailure(RuntimeError):
    pass

def class_dir_name(target_class: str) -> str:
    return Path(target_class).stem


def discover_iteration_repos(class_repo_root: Path) -> list[Path]:
    if not class_repo_root.exists():
        return []

    return sorted(
        [
            p for p in class_repo_root.iterdir()
            if p.is_dir()
            and p.name.startswith("iter-")
            and p.name.endswith("-commons-math")
        ],
        key=lambda p: int(p.name.split("-")[1]),
    )
def run_designite(
    repo_path: Path,
    project_root: Path,
    class_name: str,
    iteration_label: str,  # "baseline", "iter-01", ...
    designite_jar: Path = Path("tools/DesigniteJava/DesigniteJava.jar"),
    java_cmd: str = "java",
):
    source_dir = repo_path / "src/main/java"
    output_dir = (
        project_root
        / "analysis"
        / "designite"
        / class_name
        / iteration_label
    )

    if not designite_jar.exists():
        raise DesigniteFailure(f"Missing Designite JAR: {designite_jar}")

    if not source_dir.exists():
        raise DesigniteFailure(f"Missing source directory: {source_dir}")

    output_dir.mkdir(parents=True, exist_ok=True)

    cmd = [
        java_cmd,
        "-jar",
        str(designite_jar),
        "-i", str(source_dir),
        "-o", str(output_dir),
    ]

    print("[Designite] Running:")
    print(" ", " ".join(cmd))

    result = subprocess.run(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )

    if result.returncode != 0:
        print("----- STDOUT -----")
        print(result.stdout)
        print("----- STDERR -----")
        print(result.stderr)
        raise DesigniteFailure("DesigniteJava failed")

    print("[Designite] Results written to:", output_dir)

    return {
        "class": class_name,
        "iteration": iteration_label,
        "repo": str(repo_path),
        "output_dir": str(output_dir),
    }

PROJECT_ROOT = Path(".")
REPOS_ROOT = PROJECT_ROOT / "repos"

TARGET_CLASSES = [
    "src/main/java/org/apache/commons/math3/util/Precision.java",
    "src/main/java/org/apache/commons/math3/linear/Array2DRowRealMatrix.java",
    "src/main/java/org/apache/commons/math3/stat/descriptive/DescriptiveStatistics.java",
    "src/main/java/org/apache/commons/math3/util/MathArrays.java",
    "src/main/java/org/apache/commons/math3/optim/linear/SimplexSolver.java",
    "src/main/java/org/apache/commons/math3/util/FastMath.java"
]


for target_class in TARGET_CLASSES:
    class_name = class_dir_name(target_class)
    class_repo_root = REPOS_ROOT / class_name

    print(f"\n=== Running Designite for {class_name} ===")

    # --------------------
    # Baseline
    # --------------------
    baseline_repo = class_repo_root / "baseline-commons-math"
    if baseline_repo.exists():
        run_designite(
            repo_path=baseline_repo,
            project_root=PROJECT_ROOT,
            class_name=class_name,
            iteration_label="baseline",
        )
    else:
        print(f"[Warning] No baseline repo for {class_name}")

    # --------------------
    # Iterations (dynamic)
    # --------------------
    iteration_repos = discover_iteration_repos(class_repo_root)

    for repo_path in iteration_repos:
        iter_label = repo_path.name.replace("-commons-math", "")
        print(f"\n--- {class_name} / {iter_label} ---")

        run_designite(
            repo_path=repo_path,
            project_root=PROJECT_ROOT,
            class_name=class_name,
            iteration_label=iter_label,
        )
