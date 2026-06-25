#!/usr/bin/env python
from __future__ import annotations

import argparse
from pathlib import Path
import hashlib
import json
import pandas as pd

SENSITIVE_COLUMNS = {"annotator_name", "annotator_email", "api_request_id", "user_ip", "private_note"}


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open('rb') as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b''):
            h.update(chunk)
    return h.hexdigest()


def main() -> None:
    ap = argparse.ArgumentParser(description="Anonymize private raw ledger and create a manifest.")
    ap.add_argument("--private-ledger", required=True)
    ap.add_argument("--public-ledger", required=True)
    ap.add_argument("--manifest", required=True)
    args = ap.parse_args()

    private_path = Path(args.private_ledger)
    public_path = Path(args.public_ledger)
    public_path.parent.mkdir(parents=True, exist_ok=True)
    df = pd.read_csv(private_path)
    drop_cols = [c for c in df.columns if c in SENSITIVE_COLUMNS]
    if drop_cols:
        df = df.drop(columns=drop_cols)
    df.to_csv(public_path, index=False)
    manifest = {
        "public_ledger": str(public_path),
        "rows": int(len(df)),
        "columns": list(df.columns),
        "dropped_sensitive_columns": drop_cols,
        "sha256": sha256(public_path),
    }
    Path(args.manifest).write_text(json.dumps(manifest, indent=2), encoding='utf-8')
    print(json.dumps(manifest, indent=2))


if __name__ == "__main__":
    main()
