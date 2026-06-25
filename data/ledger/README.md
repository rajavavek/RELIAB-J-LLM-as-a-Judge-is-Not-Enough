# Ledger files

`sample_demo_ledger.csv` is a small synthetic ledger created by the offline demo judge. It is included only so readers can run the metric scripts without API keys.

For the final paper, add:

- `raw_anonymized_ledger.csv`: one row per model-item-perturbation-run execution.
- `raw_anonymized_ledger.jsonl`: optional nested version preserving provider metadata and rationales.
- `ledger_manifest.json`: run date, commit hash, model versions, item count, perturbation count, and checksum values.

Do not upload private API logs, user data, personally identifying annotator data, or copyrighted source passages unless you have permission.
