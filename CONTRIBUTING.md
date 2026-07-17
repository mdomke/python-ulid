# Contributing to python-ulid

Thank you for your interest in contributing to `python-ulid`! We appreciate all kinds of contributions: fixing bugs, improving documentation, submitting feature requests, or writing code.

This document guides you through setting up your local environment and details our development workflow and coding standards.

---

## 🚀 Getting Started

We use [uv](https://github.com/astral-sh/uv) for fast, robust package and dependency management.

### 1. Prerequisites
- **Python**: `>= 3.10`
- **uv**: Install via `curl -LsSf https://astral.sh/uv/install.sh | sh` (or your preferred package manager)

### 2. Local Setup
1. **Fork and clone** the repository:
   ```bash
   git clone https://github.com/<your-username>/python-ulid.git
   cd python-ulid
   ```

2. **Sync the dependencies**:
   This will automatically create a `.venv` virtual environment and install all packages in the developer and documentation groups:
   ```bash
   uv sync
   ```

3. **Install pre-commit hooks**:
   We use `pre-commit` to ensure code style, formatting, and static typing checks run automatically before each commit.
   ```bash
   uv run pre-commit install
   ```

---

## 🎨 Coding Standards

To maintain a clean, readable, and highly maintainable codebase, we enforce the following development standards:

### 1. Type Annotations
- **Strictly Required**: We enforce type annotations across the entire codebase. This includes all function signatures, arguments, and return types.
- **Static Analysis**: Our configuration has `disallow_untyped_defs = true` set for Mypy and uses strict `pyrefly` checks. Untyped or partially-typed code will fail the lint pipelines.
- **Example**:
  ```python
  def generate_ulid(timestamp: float | None = None) -> ULID:
      ...
  ```

### 2. Ruff Formatting & Linting
- **Formatting**: We use [Ruff](https://github.com/astral-sh/ruff) for automatic code formatting (`ruff format`).
- **Code Style**: Ruff also handles our lint checks, including import sorting (`isort`), code complexity limits (`mccabe`), and code style conventions.
- **Configuration**:
  - Line length limit: **100 characters**.
  - Imports are forced to single lines and ordered.
  - Standard Ruff defaults apply (see `.ruff_defaults.toml`).

---

## 🛠️ Development Tasks & Commands

We use [Poe the Poet](https://github.com/nat-n/poethepoet) as our task runner. You can invoke all necessary development, testing, and formatting tools through `poe` via `uv run`.

| Task | Command | Description |
| :--- | :--- | :--- |
| **All Checks** | `uv run poe check` | Run linter, formatter checks, type checking, and docs check. |
| **Formatting** | `uv run poe fmt` | Auto-format Python source files using `ruff format`. |
| **Lint** | `uv run poe check-code` | Check source files for lint and code style issues using `ruff`. |
| **Format Check** | `uv run poe check-fmt` | Dry-run format check without modifying files. |
| **Type Check** | `uv run poe check-types` | Run strict static analysis and type verification with `pyrefly`. |
| **Docs Lint** | `uv run poe check-docs` | Lint documentation style using `doc8`. |
| **Run Tests** | `uv run poe test` | Run pytest with code coverage tracking. |
| **Build Docs** | `uv run poe docs` | Build the HTML documentation locally using Sphinx. |

> [!TIP]
> Before pushing any changes or opening a Pull Request, always make sure to run the complete checks suite with **`uv run poe check`** and run the test suite with **`uv run poe test`**.

### Manual Pre-commit Execution
If you want to run all pre-commit checks against your staged or unstaged files manually:
```bash
uv run pre-commit run --all-files
```

---

## 📬 Submitting a Pull Request

1. **Create a branch** for your feature or bugfix:
   ```bash
   git checkout -b feature/my-cool-improvement
   ```
2. **Make your changes**, ensuring you write comprehensive unit tests.
3. **Format and verify** your code:
   ```bash
   uv run poe fmt
   uv run poe check
   uv run poe test
   ```
4. **Commit your changes**:
   Our pre-commit hooks will automatically trigger to verify your work.
5. **Push and open a PR** on GitHub! Please provide a descriptive title and detailed explanation of your changes in the PR description.

---

Thank you for helping make `python-ulid` better! 🌟
