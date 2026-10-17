#!/usr/bin/env python3
"""Run layer-2/smpc_bench.py over a grid of party counts n and vector lengths k, sequentially (one
configuration at a time, all parties as local processes on this host), and merge per-trial and
per-party memory results.

Profiles:
  aligned : 256-bit prime field (SecInt l=224 gives a 256-bit p in MPyC 0.9),
            TLS (--ssl) between parties, 10 warm-ups + N=100 trials
  default : MPyC defaults (SecInt l=32 -> 64-bit p, no TLS), same trial counts
"""
import argparse, csv, glob, json, os, subprocess, sys, time
ap = argparse.ArgumentParser()
ap.add_argument('--profile', choices=['aligned', 'default'], default='aligned')
ap.add_argument('--parties', default='3,4,5,6,7,8,12,16')
ap.add_argument('--ks', default='10000,50000,100000')
ap.add_argument('--trials', type=int, default=100)
ap.add_argument('--warmup', type=int, default=10)
a = ap.parse_args()
root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
l2 = os.path.join(root, 'layer-2')
raw = os.path.join(root, 'results', 'raw', a.profile)
os.makedirs(raw, exist_ok=True)
extra = ['--ssl', '--bits', '224'] if a.profile == 'aligned' else []
for k in [int(x) for x in a.ks.split(',')]:
    for n in [int(x) for x in a.parties.split(',')]:
        tag = f'{a.profile}_n{n}_k{k}'
        cmd = [sys.executable, 'smpc_bench.py', '-M', str(n), '--k', str(k), '--trials', str(a.trials),
               '--warmup', str(a.warmup), '--tag', tag, '--out-dir', raw] + extra
        t = time.time()
        p = subprocess.run(cmd, cwd=l2, capture_output=True, text=True, stdin=subprocess.DEVNULL, timeout=7200)
        with open(os.path.join(raw, f'log_{tag}.txt'), 'w') as f:
            f.write(' '.join(cmd) + '\n' + p.stdout + '\n' + p.stderr)
        print(tag, 'rc', p.returncode, f'{time.time()-t:.0f}s', [l for l in p.stdout.splitlines() if 'online' in l], flush=True)
# merge
rows = []
for f in sorted(glob.glob(os.path.join(raw, 'trials_*.csv'))):
    rows += list(csv.DictReader(open(f)))
with open(os.path.join(root, 'results', f'smpc_trials_{a.profile}.csv'), 'w', newline='') as f:
    w = csv.DictWriter(f, fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)
mem = [json.load(open(f)) for f in sorted(glob.glob(os.path.join(raw, 'mem_*.json')))]
with open(os.path.join(root, 'results', f'smpc_memory_{a.profile}.csv'), 'w', newline='') as f:
    w = csv.DictWriter(f, fieldnames=list(mem[0])); w.writeheader(); w.writerows(mem)
