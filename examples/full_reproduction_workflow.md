# Full reproduction workflow

1. Freeze the benchmark item file and record its SHA-256 checksum.
2. Validate all base items using `scripts/01_validate_items.py`.
3. Generate variants using `scripts/02_generate_variants.py`.
4. Run every judge with settings in `config/model_settings.yaml`.
5. Save one raw ledger per model and concatenate ledgers only after verifying that schemas match.
6. Run `scripts/06_make_public_release.py` to remove private metadata.
7. Compute reliability metrics with `scripts/04_compute_metrics.py`.
8. Compute confidence intervals with `scripts/05_bootstrap_ci.py`.
9. Archive the repository on Zenodo or OSF and add the DOI/link to the paper.
