#!/usr/bin/env python3
"""Run layer-2/layer2_smpc.py repeatedly for several party counts and record what it prints
(its own timer and memory figures). This script only invokes layer2_smpc.py and parses stdout."""
import csv, os, re, subprocess, sys, argparse
ap = argparse.ArgumentParser()
ap.add_argument('--parties', default='1,3,4,5,6,7,8,12,16')
ap.add_argument('--repeats', type=int, default=20)
ap.add_argument('--num_ops', type=int, default=5)  # automate_layers.py default --smpc_ops
ap.add_argument('--out', default='results/original_layer2_smpc.csv')
a = ap.parse_args()
root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
pat = {k: re.compile(v) for k, v in {
    'execution_time_s': r'Execution Time: ([0-9.]+) seconds', 'peak_ram_mb': r'Peak RAM Usage: ([0-9.]+) MB',
    'comm_bytes': r'Comm Volume Bytes: (\d+)', 'results': r'Results: (\[.*\])'}.items()}
rows = []
for m in [int(x) for x in a.parties.split(',')]:
    for r in range(a.repeats):
        p = subprocess.run([sys.executable, 'layer2_smpc.py', '--num_ops', str(a.num_ops), '-M', str(m)],
                           cwd=os.path.join(root, 'layer-2'), capture_output=True, text=True, timeout=300,
                           stdin=subprocess.DEVNULL)
        row = {'parties': m, 'repeat': r, 'num_ops': a.num_ops, 'returncode': p.returncode}
        for k, rx in pat.items():
            mm = rx.search(p.stdout)
            row[k] = mm.group(1) if mm else ''
        rows.append(row); print(row, flush=True)
os.makedirs(os.path.dirname(os.path.join(root, a.out)), exist_ok=True)
with open(os.path.join(root, a.out), 'w', newline='') as f:
    w = csv.DictWriter(f, fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)
