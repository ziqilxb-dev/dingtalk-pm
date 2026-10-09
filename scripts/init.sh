#!/bin/bash
set -euo pipefail
SKILL_SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
python3 "$SKILL_SCRIPT_DIR/initialize.py" --project "$PWD"
