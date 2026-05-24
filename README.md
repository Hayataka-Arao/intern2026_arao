# 使い方

Apache Commons Math のクラスを Claude(AIコーディングエージェント)で反復的にリファクタし、各イテレーションのコード品質を測定するパイプライン。

`scripts_new/` のスクリプトを **01 → 06 の番号順** に実行し、最後に `research_questions2.ipynb` でグラフ化する。

---

## プロジェクト構成

```
Intern/
├── scripts_new/                  # ★現行のコード（これを使う。Claude対応・拡張版）
│   ├── 01_iterate_agentic_refactor.py
│   ├── 02_run_refactoring_miner.py
│   ├── 03_run_designite.py
│   ├── 04_analyze_refactoring_miner.py
│   ├── 05_analyze_designite.py
│   ├── 06_summarize_codex_results.py
│   ├── research_questions2.ipynb        # 可視化ノートブック（最新版）
│   └── test_prompt.py                   # Claude CLI 疎通確認用
│
├── scripts/                      # 拡張前の旧コード（Codexのみ対応）。基本使わない
│
├── tools/                        # 分析用の外部Javaツール（JDK 21+ で実行）
│   ├── RefactoringMiner/         #   bin/ と lib/
│   └── DesigniteJava/
│       └── DesigniteJava.jar
│
├── repos/                        # 各イテレーションの commons-math リポジトリ実体
│   ├── baseline-commons-math/    #   共通ベースライン（git付き）
│   └── claude/<クラス名>/         #   エージェント別 × クラス別
│       ├── baseline-commons-math/
│       └── iter-NN-commons-math/ #   イテレーションごとにクローン（git履歴あり）
│
├── analysis/                     # 分析の入出力
│   ├── claude-artifacts/<クラス名>/iter-NN-claude.json   # 01 の実行記録
│   ├── codex-artifacts/          #   （Codex用。今回は未実行）
│   ├── RefactoringMiner/claude/<クラス名>/summary_refactorings.csv  # 02→04 の出力
│   ├── designite/claude/<クラス名>/                       # 03→05 の出力
│   │   ├── baseline/ , iter-NN/  #     Designite 生データ
│   │   ├── designite_smells_long.csv
│   │   └── designite_type_metrics.csv
│   └── experiment_summary.csv    # 06 の出力（全体サマリ）
│
├── データ結果/                    # 結果・出力データの保管フォルダ
├── インターンシップ報告.pptx       # 報告プレゼン
├── .env                          # API　KEY を格納
├── .gitignore
└── README.md
```

> **`scripts_new` と `scripts` の違い**
> `scripts_new/` が現行のコードで、Claude に対応した拡張版。**実行にはこちらを使う。**
> `scripts/` は拡張前の旧コードで、Codex のみ対応。参照用に残してあるが通常は使わない。
>
> **旧データの混在に注意**
> `analysis/designite/` と `analysis/RefactoringMiner/` の直下にある、`claude/` 以外のクラス名フォルダや `old iters/` は**古い実行結果**。現行データは必ず `<tool>/claude/<クラス名>/` を参照すること。

---

## ⚠️ 事前準備（これを間違えると動かない）

### 1. JDK を2つ用意し、工程ごとに切り替える

このパイプラインは **2つの異なる JDK を使い分ける**。

| 実行するスクリプト | 必要な JDK |
|------|-----------|
| `01`（commons-math のビルド・テスト） | **JDK 8** |
| `02`, `03`（RefactoringMiner / Designite） | **JDK 21 以上** |

PowerShell での切り替え:
```powershell
# 01 を実行する前（JDK 8 に切り替え）
$env:JAVA_HOME = "C:\Program Files\Eclipse Adoptium\jdk-8.0.xxx-hotspot"
$env:Path = "$env:JAVA_HOME\bin;$env:Path"
mvn --version    # Java version が 1.8 になっていることを確認

# 02 / 03 を実行する前（JDK 21+ に切り替え。例: 25）
$env:JAVA_HOME = "C:\Program Files\Eclipse Adoptium\jdk-25.x.x-hotspot"
$env:Path = "$env:JAVA_HOME\bin;$env:Path"
java -version    # 25 などになっていることを確認
```
> JDK バージョンはターミナルを開き直すとリセットされる。各工程の前に毎回設定すること。

### 2. `.env` に API キーを置く（クォートで囲まない）

ルートの `.env` に以下を記載。**ダブルクォートを付けるとキーが無効になる**ので注意。
```
ANTHROPIC_API_KEY=sk-ant-xxxxxxxx
```

### 3. その他の前提

- Python 3.x（`.venv/` の仮想環境を有効化して使う）
- Maven（commons-math のテスト実行に使用）
- Claude CLI（`claude.cmd` が PATH 上にあること。`claude -p "hi"` で疎通確認できる）
- 外部ツールは `tools/` に同梱（RefactoringMiner, DesigniteJava.jar）
- git のコミット署名でパスフレーズを毎回聞かれる場合:
  ```powershell
  git config --global commit.gpgsign false
  ```

---

## 実行手順

```powershell
cd C:\Users\ppen6\Documents\Intern

# .venv を有効化
.\.venv\Scripts\Activate.ps1

# === JDK 8 に切り替え（事前準備1参照）===

# 1. エージェントで反復リファクタを実行
python .\scripts_new\01_iterate_agentic_refactor.py

# === JDK 21+ に切り替え ===

# 2. RefactoringMiner でリファクタ種別を検出
python .\scripts_new\02_run_refactoring_miner.py

# 3. Designite でコードスメル・メトリクスを測定
python .\scripts_new\03_run_designite.py

# 4-6. 集計して分析用 CSV を生成
python .\scripts_new\04_analyze_refactoring_miner.py
python .\scripts_new\05_analyze_designite.py
python .\scripts_new\06_summarize_codex_results.py
```

### 7. 可視化

`scripts_new/research_questions2.ipynb` を Jupyter / VS Code で開き、上から順に実行する。
`analysis/` 配下の集計 CSV を読んでグラフを表示する。先頭セルの作業ディレクトリ設定（`analysis/` への移動）は環境に合わせて確認すること。

---

## 各スクリプトの役割

| ファイル | 内容 |
|---------|------|
| `01_iterate_agentic_refactor.py` | 各クラスをクローン → Claude でリファクタ → テスト検証 → commit を、収束または最大20回まで繰り返す |
| `02_run_refactoring_miner.py` | 各イテレーション間のコミット差分から、適用されたリファクタ種別を検出 |
| `03_run_designite.py` | 各イテレーションのコードに対しコードスメルと型メトリクスを測定 |
| `04_analyze_refactoring_miner.py` | 02 の出力を集計して `summary_refactorings.csv` を生成 |
| `05_analyze_designite.py` | 03 の出力を集計して `designite_*.csv` を生成 |
| `06_summarize_codex_results.py` | 実験全体のサマリ `experiment_summary.csv` を生成 |
| `research_questions2.ipynb` | 上記 CSV を読み込んでグラフ化 |
| `test_prompt.py` | Claude CLI の疎通確認用デバッグスクリプト |

---

## 入出力の場所

- **入力リポジトリ**: `repos/baseline-commons-math/`（共通ベースライン）
- **リファクタ実体**: `repos/claude/<クラス名>/iter-NN-commons-math/`（イテレーションごと、git履歴つき）
- **実行記録**: `analysis/claude-artifacts/<クラス名>/iter-NN-claude.json`
- **リファクタ検出結果**: `analysis/RefactoringMiner/claude/<クラス名>/summary_refactorings.csv`
- **品質測定結果**: `analysis/designite/claude/<クラス名>/`（生データ + 集計 CSV）
- **全体サマリ**: `analysis/experiment_summary.csv`

---

## 対象クラスの変更

対象クラス: `Precision` / `FastMath` / `MathArrays` / `Array2DRowRealMatrix` / `DescriptiveStatistics` / `SimplexSolver`（Apache Commons Math 3.6.1）

対象クラスや最大イテレーション数を変えるには、`01_iterate_agentic_refactor.py` 末尾の `TARGET_CLASSES` と `MAX_ITERS` を編集する。
