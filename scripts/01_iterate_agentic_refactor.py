import subprocess
import json
from pathlib import Path
from datetime import datetime
import shutil
from enum import Enum

# -----------------------------
# Exceptions
# -----------------------------


class CodexFailure(Enum):
    TIMEOUT = "timeout"
    CODEX_ERROR = "codex_error"
    TESTS_MODIFIED = "tests_modified"
    NO_CHANGES = "no_changes"
    UNEXPECTED_SCOPE = "unexpected_scope"


class CodexExecutionError(Exception):
    def __init__(self, returncode, stdout, stderr):
        self.returncode = returncode
        self.stdout = stdout
        self.stderr = stderr
        super().__init__("Codex execution failed")

class TestFailure(RuntimeError):
    pass

# -----------------------------
# Helper functions
# -----------------------------
def assert_codex_available():
    """Ensure 'codex' CLI is installed and callable"""
    try:
        subprocess.run(["codex", "--help"], capture_output=True, text=True, check=True)
    except Exception:
        raise RuntimeError("Codex CLI not available")

def class_dir_name(target_class: str) -> str:
    return Path(target_class).stem

def ensure_class_baseline(
    project_root: Path,
    baseline_repo: str,
    target_class: str,
):
    """
    Ensure repos/<ClassName>/baseline-commons-math exists.
    """
    repos_dir = project_root / "repos"
    class_dir = repos_dir / class_dir_name(target_class)
    class_dir.mkdir(parents=True, exist_ok=True)

    dst = class_dir / baseline_repo
    if dst.exists():
        return

    src = repos_dir / baseline_repo
    if not src.exists():
        raise FileNotFoundError(f"Global baseline not found: {src}")

    print(f"[Baseline] Initializing baseline for {class_dir.name}")
    shutil.copytree(src, dst)


def clone_commons_math_iteration(
    project_root: Path,
    source_repo: str,
    target_iter: int,
    target_class: str,
) -> Path:
    """
    Clone baseline or previous iteration into a class-scoped iteration folder.

    Layout:
      repos/<ClassName>/baseline-commons-math
      repos/<ClassName>/iter-01-commons-math
      ...
    """
    repos_dir = project_root / "repos"
    class_dir = repos_dir / class_dir_name(target_class)
    class_dir.mkdir(parents=True, exist_ok=True)

    src = class_dir / source_repo
    dst = class_dir / f"iter-{target_iter:02d}-commons-math"

    if not src.exists():
        raise FileNotFoundError(f"Source repo not found: {src}")
    if dst.exists():
        raise FileExistsError(f"Target iteration already exists: {dst}")

    print(f"[Clone] {src.relative_to(repos_dir)} → {dst.relative_to(repos_dir)}")
    shutil.copytree(src, dst)
    return dst


def git_changed_files(repo_path: Path) -> list[str]:
    """Return a list of files changed in the repo (uncommitted)"""
    result = subprocess.run(
        ["git", "status", "--porcelain"],
        cwd=repo_path,
        capture_output=True,
        text=True
    )
    return [line[3:] for line in result.stdout.splitlines()]


def assert_tests_unchanged(repo_path: Path):
    changed = git_changed_files(repo_path)
    test_changes = [f for f in changed if f.startswith("src/test/")]
    if test_changes:
        raise RuntimeError(f"Test files modified: {test_changes}")

#changes must be committed for RefactoringMiner to work
def git_commit_changes(repo_path: Path, message: str):
    """
    Commit all current changes in the repo.    
    """
    subprocess.run(
        ["git", "add", "-A"],
        cwd=repo_path,
        check=True,
    )

    result = subprocess.run(
        ["git", "commit", "-m", message],
        cwd=repo_path,
        capture_output=True,
        text=True,
    )

    if result.returncode != 0:
        raise RuntimeError(
            f"Git commit failed:\nSTDOUT:\n{result.stdout}\nSTDERR:\n{result.stderr}"
        )


# -----------------------------
# Codex integration
# -----------------------------
def run_codex_with_retries(repo_path: Path, target_class: str, max_retries: int = 2, timeout_sec: int = 300):
    """Run codex CLI to refactor a class, return explanation string"""
    import textwrap

    prompt = textwrap.dedent(f"""
        You are refactoring a mature Java library: Apache Commons Math.

        Target:
        Refactor the class {target_class}.

        Hard constraints:
        - Java compatibility constraint:
            * The code MUST remain compatible with Java 6 / Java 7 APIs.
            * DO NOT use any Java 8+ language features or standard library methods.
            * In particular, do NOT use java.util.Objects, Optional, streams, lambdas,
                or any methods introduced in Java 8 (e.g., Integer.toUnsignedLong).
        - DO NOT modify any files under src/test/
        - DO NOT change public APIs or method signatures
        - DO NOT change numerical behavior or tolerances
        - DO NOT add new dependencies
        - DO NOT move or rename the class

        Allowed:
        - Extract private helper methods
        - Improve internal readability
        - Reduce duplication
        - Reorder methods if helpful

        Process:
        1. Locate the target class yourself.
        2. Read the entire file before editing.
        3. Determine appropriate refactorings. If no refactorings are needed, respond with "No changes needed."
        4. If refactorings are needed, apply refactorings incrementally.
        5. Briefly explain what you changed.

        Make sure that all existing tests must pass unchanged.
        Begin.
    """).strip()

    for attempt in range(1, max_retries + 1):
        try:
            result = subprocess.run(
                ["codex", "exec", "--full-auto", prompt],
                cwd=repo_path,
                text=True,
                capture_output=True,
                timeout=timeout_sec
            )
        except subprocess.TimeoutExpired:
            if attempt == max_retries:
                raise CodexExecutionError(-1, "", "Timeout")
            continue

        if result.returncode != 0:
            if attempt == max_retries:
                raise CodexExecutionError(result.returncode, result.stdout, result.stderr)
            continue

        return result.stdout

    raise CodexExecutionError(-1, "", "Unknown error")


# -----------------------------
# Maven test integration
# -----------------------------

def infer_test_pattern(target_class_path: str) -> str:
    """
    Convert a production class path into a Maven Surefire test pattern.

    Example:
      src/main/java/org/apache/commons/math3/util/Precision.java
      -> *Precision*
    """
    class_name = Path(target_class_path).stem
    return f"*{class_name}*"


def find_test_file(repo_path: Path, target_class_path: str) -> Path | None:
    """
    Check if a corresponding test class exists in src/test/java.
    Returns the Path if found, None otherwise.
    """
    try:
        rel_path = Path(target_class_path).relative_to("src/main/java")
    except ValueError:
        rel_path = Path(target_class_path)

    test_file = repo_path / "src/test/java" / rel_path.with_name(rel_path.stem + "Test.java")
    return test_file if test_file.exists() else None


def run_tests_for_target_class(
    repo_path: Path,
    target_class_path: str,
    mvn_cmd: str = "mvn",
    timeout_sec: int = 600,
    quiet: bool = True,
):
    """
    Run Maven tests related to a target class using Surefire -Dtest.

    Returns a dictionary:
      - test_pattern: the Maven test pattern
      - passed: bool
      - stdout: captured stdout
      - stderr: captured stderr
      - skipped: True if no test class exists
    """

    if not (repo_path / "pom.xml").exists():
        raise TestFailure(f"No pom.xml found in {repo_path}")

    test_file = find_test_file(repo_path, target_class_path)
    test_pattern = infer_test_pattern(target_class_path)

    if test_file is None:
        print(f"[Warning] No corresponding test class found for {target_class_path}. Skipping tests.")
        return {
            "test_pattern": test_pattern,
            "passed": True,  # skipping counts as “pass” for automation
            "stdout": "",
            "stderr": "",
            "skipped": True,
        }

    cmd = [
        mvn_cmd,
        f"-Dtest={test_pattern}",
        "test",
    ]
    if quiet:
        cmd.insert(1, "-q")  # insert after mvn

    print("[Tests] Running:")
    print(" ", " ".join(cmd))
    print(f"[Tests] Test pattern: {test_pattern}")

    try:
        result = subprocess.run(
            cmd,
            cwd=repo_path,
            capture_output=True,
            text=True,
            timeout=timeout_sec,
        )
    except subprocess.TimeoutExpired:
        raise TestFailure("Test execution timed out")

    passed = result.returncode == 0

    if not passed:
        print("----- STDOUT -----")
        print(result.stdout)
        print("----- STDERR -----")
        print(result.stderr)

    return {
        "test_pattern": test_pattern,
        "passed": passed,
        "stdout": result.stdout,
        "stderr": result.stderr,
        "skipped": False,
    }


# -----------------------------
# Single iteration experiment
# -----------------------------
def run_refactoring_experiment(
    project_root: Path,
    source_repo: str,
    iteration: int,
    target_class: str,
    mvn_cmd: str = "mvn",
    quiet = True
):
    class_name = Path(target_class).stem  # e.g. "Precision"

    analysis_dir = (
        project_root
        / "analysis"
        / "codex-artifacts"
        / class_name
    )
    analysis_dir.mkdir(parents=True, exist_ok=True)


    metadata = {
        "iteration": iteration,
        "source_repo": source_repo,
        "target_class": target_class,
        "timestamp": datetime.now().isoformat(),
        "status": "success",
        "failure": None,
        "changed_files": [],
        "explanation": None,
        "tests": None,
        "codex": None,
    }

    try:
        assert_codex_available()

        ensure_class_baseline(
            project_root=project_root,
            baseline_repo=source_repo,
            target_class=target_class,
        )

        repo_path = clone_commons_math_iteration(
            project_root=project_root,
            source_repo=source_repo,
            target_iter=iteration,
            target_class=target_class,
        )


        print(f"[Experiment] Running Codex refactor (iter {iteration})...")
        explanation = run_codex_with_retries(
            repo_path=repo_path,
            target_class=target_class
        )

        print("[Experiment] Verifying test files unchanged...")
        assert_tests_unchanged(repo_path)

        changed_files = git_changed_files(repo_path)
        if not changed_files:
            raise RuntimeError(CodexFailure.NO_CHANGES.value)

        metadata["changed_files"] = changed_files
        metadata["explanation"] = explanation

        print("[Experiment] Running Maven tests for target class...")
        test_results = run_tests_for_target_class(
            repo_path=repo_path,
            target_class_path=target_class,
            mvn_cmd=mvn_cmd,
            quiet=quiet
        )
        metadata["tests"] = test_results

        commit_message = (
            f"Codex refactor iteration {iteration}: "
            f"{Path(target_class).name}"
        )

        print("[Experiment] Committing Codex changes...")
        git_commit_changes(
            repo_path=repo_path,
            message=commit_message,
        )

    except CodexExecutionError as e:
        metadata["status"] = "failure"
        metadata["failure"] = e.args[0]
        metadata["codex"] = {
            "returncode": e.returncode,
            "stdout": e.stdout,
            "stderr": e.stderr,
        }

    except TestFailure as e:
        metadata["status"] = "failure"
        metadata["failure"] = f"Maven tests failed: {str(e)}"

    except RuntimeError as e:
        metadata["status"] = "failure"
        metadata["failure"] = str(e)

    out = analysis_dir / f"iter-{iteration:02d}-codex.json"
    with open(out, "w") as f:
        json.dump(metadata, f, indent=2)

    print(f"[Experiment] Artifact written → {out}")
    return metadata

# -----------------------------
# Loop for N iterations
# -----------------------------
def run_experiment_iterations(
    project_root: Path,
    baseline_repo: str,
    target_class: str,
    max_iterations: int = 5,
    mvn_cmd: str = "mvn",
    quiet=True,
):
    class_baseline = baseline_repo
    last_source = class_baseline

    for iteration in range(1, max_iterations + 1):
        print(f"\n=== {class_dir_name(target_class)} | Iteration {iteration} ===")

        metadata = run_refactoring_experiment(
            project_root=project_root,
            source_repo=last_source,
            iteration=iteration,
            target_class=target_class,
            mvn_cmd=mvn_cmd,
            quiet=quiet,
        )

        if metadata["status"] != "success":
            print(f"[Experiment] Stopping at iteration {iteration} due to failure.")
            print("Failure reason:", metadata["failure"])
            
            
        tests_failed = (
            metadata.get("tests") is not None
            and not metadata["tests"].get("passed", True)
        )

        if metadata["status"] != "success" or tests_failed:
            print(f"[Experiment] Stopping at iteration {iteration}.")

            if tests_failed:
                print("[Experiment] Reason: tests failed (changes were committed).")
            elif metadata.get("failure"):
                print("[Experiment] Reason:", metadata["failure"])

            break

        if metadata.get("explanation", "").strip() == "No changes needed.":
            print(
                f"[Experiment] Stopping at iteration {iteration}: "
                "no further refactorings possible."
            )
            break

        last_source = f"iter-{iteration:02d}-commons-math"

    print(f"\n[Experiment] Finished for {class_dir_name(target_class)}")

# -----------------------------

# Main execution
PROJECT_ROOT = Path(".")
BASELINE_REPO = "baseline-commons-math"
# TARGET_CLASS = "src/main/java/org/apache/commons/math3/util/Precision.java"
MAX_ITERS = 20

# run_experiment_iterations(
#     project_root=PROJECT_ROOT,
#     baseline_repo=BASELINE_REPO,
#     target_class=TARGET_CLASS,
#     max_iterations=MAX_ITERS,
#     quiet = False
# )

TARGET_CLASSES = [
    "src/main/java/org/apache/commons/math3/util/Precision.java",
    "src/main/java/org/apache/commons/math3/linear/Array2DRowRealMatrix.java",
    "src/main/java/org/apache/commons/math3/stat/descriptive/DescriptiveStatistics.java",
    "src/main/java/org/apache/commons/math3/util/MathArrays.java",
    "src/main/java/org/apache/commons/math3/optim/linear/SimplexSolver.java",
    "src/main/java/org/apache/commons/math3/util/FastMath.java"
]

for target_class in TARGET_CLASSES:
    run_experiment_iterations(
        project_root=PROJECT_ROOT,
        baseline_repo=BASELINE_REPO,
        target_class=target_class,
        max_iterations=MAX_ITERS,
        quiet=False,
    )


