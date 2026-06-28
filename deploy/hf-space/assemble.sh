#!/usr/bin/env bash
# Assemble the curated, PII-free Hugging Face Space tree into deploy/hf-space/space/.
# Builds a fresh silver db from bronze, scrubs names/bibs, and copies only what the
# Docker image needs — no bronze PDFs, no personal data. Run from anywhere.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
HF="$ROOT/deploy/hf-space"
STAGE="$HF/space"
AGENT="$ROOT/agents/01-stateless"
PY="$AGENT/.venv/bin/python"

rm -rf "$STAGE"
mkdir -p "$STAGE/agents/01-stateless/data/silver" "$STAGE/packages"

# 1. Build + scrub silver into the staging tree (from the committed bronze).
( cd "$AGENT" && "$PY" - "$STAGE/agents/01-stateless/data/silver/cork.db" <<'PY'
import sys
from pathlib import Path
from backend import silver
db = Path(sys.argv[1])
n = silver.build_silver(db)
silver.scrub_pii(db)
print(f"built + scrubbed silver: {n} rows -> {db}")
PY
)

# 2. Copy the agent code (no bronze, venv, caches, output, .env, or full silver).
rsync -a \
  --exclude='.venv' --exclude='__pycache__' --exclude='*.pyc' --exclude='.DS_Store' \
  --exclude='output' --exclude='.env' \
  --exclude='data/bronze' --exclude='data/silver' \
  "$AGENT/" "$STAGE/agents/01-stateless/"

# 3. Copy the only shared package.
rsync -a --exclude='__pycache__' --exclude='*.pyc' --exclude='.DS_Store' \
  "$ROOT/packages/racedata/" "$STAGE/packages/racedata/"

# 4. Space-root files (Dockerfile must be at the Space root for HF to build it).
cp "$HF/Dockerfile" "$STAGE/Dockerfile"
cp "$HF/README.md" "$STAGE/README.md"
cp "$HF/.dockerignore" "$STAGE/.dockerignore"

echo
echo "Staged PII-free Space tree at: $STAGE"
echo "Sanity: rows with a name should be 0 ->"
"$PY" -c "import sqlite3; c=sqlite3.connect('$STAGE/agents/01-stateless/data/silver/cork.db'); print('  names:', c.execute(\"SELECT COUNT(*) FROM finishers WHERE name!=''\").fetchone()[0])"
