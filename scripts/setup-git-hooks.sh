#!/usr/bin/env bash
# Configure git to use .githooks for automated pre-commit quality checks.
set -euo pipefail

project_dir="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$project_dir"

chmod +x .githooks/pre-commit
git config core.hooksPath .githooks
echo "ALPORA Git hooks successfully configured: git commit will now automatically run Ruff and ./scripts/check."
