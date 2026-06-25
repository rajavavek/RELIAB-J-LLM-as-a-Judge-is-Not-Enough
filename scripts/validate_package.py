#!/usr/bin/env python3
import csv, json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

def count_rows(path):
    with open(path, newline='', encoding='utf-8') as f:
        return sum(1 for _ in csv.DictReader(f))

checks = {
    'base_items': (ROOT/'data/benchmark/base_items.csv', 1200),
    'perturbation_variants': (ROOT/'data/benchmark/perturbation_variants.csv', 12000),
    'reconstructed_evaluation_ledger': (ROOT/'data/evaluation/reconstructed_evaluation_ledger.csv', 84000),
    'domain_statistics': (ROOT/'data/benchmark/domain_statistics.csv', 10),
    'reliability_profiles': (ROOT/'data/results/reliability_profiles.csv', 8),
}

failed = []
for name, (path, expected) in checks.items():
    actual = count_rows(path)
    print(f'{name}: {actual} rows (expected {expected})')
    if actual != expected:
        failed.append((name, actual, expected))

manifest = json.loads((ROOT/'metadata/manifest.json').read_text(encoding='utf-8'))
print('Package:', manifest['package_title'])
print('Version:', manifest['version'])

if failed:
    raise SystemExit(f'Validation failed: {failed}')
print('Validation passed.')
