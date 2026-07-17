# Contributing to python-ulid

Thank you for your interest in contributing to `python-ulid`! We appreciate all kinds of contributions: fixing bugs, improving documentation, submitting feature requests, or writing code.

This document guides you through setting up your local environment and details our development workflow and coding standards.

---

## 🚀 Getting Started

We support two ways to set up your local development environment: **Flox** (recommended, zero-configuration setup) or a **Manual** setup.

### Option 1: Using Flox (Recommended)

If you have [Flox](https://flox.dev/) installed, setting up your environment is completely automated. Flox will automatically handle installing `uv`, Python, project dependencies, and pre-commit hooks inside a reproducible environment.

1. **Fork and clone** the repository:
   ```bash
   git clone https://github.com/<your-username>/python-ulid.git
   cd python-ulid
   ```

2. **Activate the Flox environment**:
   ```bash
   flox activate
   ```
   That's it! Flox automatically sets up everything for you and activates your python virtual environment.

---

### Option 2: Manual Setup

If Flox is not an option, you can set up your environment manually. We use [uv](https://github.com/astral-sh/uv) for fast, robust package and dependency management.

1. **Prerequisites**:
   - **Python**: `>= 3.10`
   - **uv**: Install via `curl -LsSf https://astral.sh/uv/install.sh | sh` (or your preferred package manager)

2. **Fork and clone** the repository:
   ```bash
   git clone https://github.com/<your-username>/python-ulid.git
   cd python-ulid
   ```

3. **Sync the dependencies**:
   This will automatically create a `.venv` virtual environment and install all packages in the developer and documentation groups:
   ```bash
   uv sync
   ```

4. **Install pre-commit hooks**:
   We use `prek` (a fast, Rust-based alternative to pre-commit) to manage our Git hooks, ensuring code style, formatting, and static typing checks run automatically before each commit.
   ```bash
   uv run prek install
   ```

---

## 🛠️ Development Tasks & Commands

We use [Poe the Poet](https://github.com/nat-n/poethepoet) as our task runner. Depending on how you set up your development environment, you can invoke the tasks directly or via `uv run`:

- **With Flox (Recommended)**: Since the virtual environment is automatically activated in your shell, you can run all commands directly:
  ```bash
  poe test
  ```
- **With Manual Setup**: If you did not use Flox, prefix all tasks with `uv run`:
  ```bash
  uv run poe test
  ```
  (You can also manually activate the virtual environment to get the same shorthands as above).

### Common Development Tasks

| Task | Command (Flox) | Command (Manual) | Description |
| :--- | :--- | :--- | :--- |
| **All Checks** | `poe check` | `uv run poe check` | Run linter, formatter checks, type checking, and docs check. |
| **Formatting** | `poe fmt` | `uv run poe fmt` | Auto-format Python source files using `ruff format`. |
| **Lint** | `poe check-code` | `uv run poe check-code` | Check source files for lint and code style issues using `ruff`. |
| **Format Check** | `poe check-fmt` | `uv run poe check-fmt` | Dry-run format check without modifying files. |
| **Type Check** | `poe check-types` | `uv run poe check-types` | Run strict static analysis and type verification with `pyrefly`. |
| **Docs Lint** | `poe check-docs` | `uv run poe check-docs` | Lint documentation style using `doc8`. |
| **Run Tests** | `poe test` | `uv run poe test` | Run pytest with code coverage tracking. |
| **Build Docs** | `poe docs` | `uv run poe docs` | Build the HTML documentation locally using Sphinx. |

> [!TIP]
> Before pushing any changes or opening a Pull Request, always make sure to run the complete checks suite with **`poe check`** (or `uv run poe check`) and run the test suite with **`poe test`** (or `uv run poe test`).

### Manual Hook Execution with prek

If you want to run all checks against your staged or unstaged files manually:

- **With Flox**:
  ```bash
  prek run --all-files
  ```
- **With Manual Setup**:
  ```bash
  uv run prek run --all-files
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

## 📬 Submitting a Pull Request

1. **Create a branch** for your feature or bugfix:
   ```bash
   git checkout -b feature/my-cool-improvement
   ```
2. **Make your changes**, ensuring you write comprehensive unit tests.
3. **Format and verify** your code (e.g. using `poe` directly if using Flox, or prefixed with `uv run` if manual):
   ```bash
   poe fmt
   poe check
   poe test
   ```
4. **Commit your changes**:
   Our pre-commit hooks will automatically trigger to verify your work.
5. **Push and open a PR** on GitHub! Please provide a descriptive title and detailed explanation of your changes in the PR description.

---

Thank you for helping make `python-ulid` better! 🌟
