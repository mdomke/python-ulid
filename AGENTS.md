# Guidelines for AI Coding Agents

Welcome! If you are an AI assistant, coding agent, or language model (e.g., Antigravity, Claude Code, Cursor, Copilot) helping to develop `python-ulid`, please adhere to the guidelines in this document.

These instructions ensure consistency, prevent common development errors, and keep code quality aligned with the project's standards.

---

## 🏗️ Project Stack & Tooling

We use modern, fast, and strict tooling for Python development. Always use the specified commands below.

- **Dependency Manager**: We use **[uv](https://github.com/astral-sh/uv)**.
  - Do *not* use raw `pip`, `poetry`, or `pdm`.
  - To install dependencies, run: `uv sync`.
  - Always prefix commands with `uv run` to execute them in the correct environment (e.g., `uv run pytest`).
- **Task Runner**: We use **[Poe the Poet](https://github.com/nat-n/poethepoet)**.
  - Development tasks are defined in `pyproject.toml` under `[tool.poe.tasks]`.
  - Run checks with `uv run poe check`.
- **Linting & Formatting**: We use **[Ruff](https://github.com/astral-sh/ruff)**.
  - Standard line-length limit is **100 characters**.
  - Auto-format code using `uv run poe fmt`.
- **Static Typing**: We use **[pyrefly](https://github.com/mdomke/pyrefly)** for strict static analysis.
  - Run type checking using `uv run poe check-types`.

---

## 🎯 Coding Standards for Agents

### 1. Mandatory Type Annotations
We require full, strict type annotations across the entire codebase.
- **Rules**:
  - Always annotate all function parameters and return values.
  - Avoid `Any` where possible; use specific types, unions, or generics.
  - Run type checking to verify compliance: `uv run poe check-types`.

### 2. Ruff Compliance
- **Formatting**: Run formatting before finalizing any file modifications.
  - Use `uv run poe fmt` to auto-format.
  - Code style rules are detailed in `pyproject.toml` and `.ruff_defaults.toml`.
- **Imports**: We use single-line imports and specific import order (`isort` rules). Let Ruff handle this automatically.

### 3. Production-Ready Code Only
- Never generate code with comments like `# TODO: implement this`, `# placeholder`, or partial code blocks.
- Implement the full logic requested, ensuring error handling and correct edge cases are covered.

---

## 🛠️ Verification Workflow

Before completing any task, you **MUST** run the verification commands to ensure no regressions or style issues are introduced.

1. **Format Code**:
   ```bash
   uv run poe fmt
   ```
2. **Run Lints, Types & Style Checks**:
   ```bash
   uv run poe check
   ```
3. **Run Test Suite**:
   ```bash
   uv run poe test
   ```

Make sure all checks pass without errors.

---

## 📂 Codebase Navigation

- **`/ulid`**: Contains the source code of the `python-ulid` package.
- **`/tests`**: Contains all unit and integration tests. Write corresponding test cases here for any new logic.
- **`/docs`**: Contains Sphinx-based documentation.
- **`pyproject.toml`**: The single source of truth for dependencies, tools configuration, and Poe tasks.

Refer to the primary developer documentation and [CONTRIBUTING.md](file:///Users/martin.domke/Source/private/ulid/CONTRIBUTING.md) for more details.
