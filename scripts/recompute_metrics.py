#!/usr/bin/env python3
import argparse, csv
from collections import defaultdict

parser = argparse.ArgumentParser(description='Recompute simple accuracy metrics from a RELIAB-J evaluation ledger.')
parser.add_argument('--ledger', required=True, help='Path to reconstructed_evaluation_ledger.csv')
parser.add_argument('--out', required=True, help='Output CSV path')
args = parser.parse_args()

counts = defaultdict(lambda: [0, 0])
with open(args.ledger, newline='', encoding='utf-8') as f:
    for row in csv.DictReader(f):
        key = (row['judge_model'], row['domain'])
        counts[key][1] += 1
        if row['correct'].lower() == 'true':
            counts[key][0] += 1

with open(args.out, 'w', newline='', encoding='utf-8') as f:
    w = csv.writer(f)
    w.writerow(['judge_model','domain','correct','total','accuracy'])
    for (model, domain), (correct, total) in sorted(counts.items()):
        w.writerow([model, domain, correct, total, round(correct/total, 6)])
print(f'Wrote {args.out}')
