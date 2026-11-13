#!/usr/bin/env bash
# TPS / latency sweep chart (output/charts/chart6_tps_latency_multi.png) using
# automate_layers.run_tps_latency_sweep and automate_layers.save_tps_latency_chart.
# This file is a bash script with an embedded Python program; run it with:  bash tps.py
# MDCOLAB_DIR selects the repository directory (default: the directory containing this file).
# The sweep needs a running Fabric test-network (layer-3/README.md).
MDCOLAB_DIR="${MDCOLAB_DIR:-$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)}"
export MDCOLAB_DIR
"${PYTHON:-python3}" - << 'PY'
import os, re, sys
base_dir = os.environ['MDCOLAB_DIR']
report = os.path.join(base_dir, 'metrics_report.md')
vals = {}
if os.path.exists(report):
    with open(report, 'r') as f:
        for line in f:
            m = re.match(r"\|\s*(.*?)\s*\|\s*([0-9A-Za-z\.]+)\s*\|", line)
            if m:
                k = m.group(1).strip()
                v = m.group(2).strip()
                try:
                    vals[k] = float(v)
                except Exception:
                    vals[k] = v
sys.path.append(base_dir)
import automate_layers as al
rates = [50, 100, 150, 200, 250]
counts = [1, 2, 3]
zeros = {c: [{'arrival': r, 'tps': 0.0, 'lat': 0.0} for r in rates] for c in counts}
problems = al.check_fabric(base_dir, need_script=False)
if problems:
    # No usable Fabric network: draw the chart with zero values so the plotting path can still be checked.
    print('Fabric test-network not available, chart drawn with zero values:')
    for p in problems:
        print('  -', p)
    sweep = zeros
else:
    try:
        sweep = al.run_tps_latency_sweep(base_dir, rates, counts)
    except Exception as e:
        print(f'TPS sweep did not run ({type(e).__name__}: {e}); chart drawn with zero values')
        sweep = zeros
ok = al.save_tps_latency_chart(base_dir, sweep)
print('OK' if ok else 'FAIL')
for ext in ('png', 'txt'):
    p = os.path.join(base_dir, 'output', 'charts', f'chart6_tps_latency_multi.{ext}')
    print(p, os.path.exists(p))
PY
