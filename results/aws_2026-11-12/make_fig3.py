#!/usr/bin/env python3
"""Figure 3: Fabric committed TPS (bars) and mean finality (dots), one factor at a time.

Usage:  python make_tables.py && python make_fig3.py [RUN_DIR]
Reads   RUN_DIR/tables/fig3_values.csv
Writes  RUN_DIR/figures/fig3_fabric.png (600 dpi)
Needs   matplotlib.
Common condition: offered 100 tx/s for 60 s, 64 peer-CLI clients, BatchTimeout 2 s; baseline = block size
(MaxMessageCount) 10, majority endorsement, 2 organisations.
"""
import csv, os, sys
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

ROOT = os.path.abspath(sys.argv[1] if len(sys.argv) > 1 else os.path.dirname(os.path.abspath(__file__)))
rows = list(csv.DictReader(open(os.path.join(ROOT, 'tables', 'fig3_values.csv'))))
labels = [r['label'].replace(' (baseline)', '\n(baseline)').replace('Block ', 'Block\n').replace('Orgs ', 'Orgs\n') for r in rows]
tps = [float(r['tps_committed']) for r in rows]
fin = [float(r['finality_mean_s']) for r in rows]
plt.rcParams.update({'font.family': 'serif', 'font.size': 7.5, 'xtick.labelsize': 7, 'ytick.labelsize': 7, 'axes.labelsize': 8})
N = len(rows)
fig, ax = plt.subplots(figsize=(3.25, 1.75))
ax2 = ax.twinx()
ax.bar(range(N), tps, color='#9cc3e6', ec='#333333', lw=0.4, width=0.68)
for i, v in enumerate(tps):
    ax.text(i, v / 2, f'{v:.1f}', ha='center', va='center', rotation=90, fontsize=7, color='#0b2f57')
ax2.plot(range(N), fin, 'o', color='#c0392b', ms=3.6)
for i, v in enumerate(fin):
    ax2.annotate(f'{v:.2f}', (i, v), textcoords='offset points', xytext=(0, 3.5), ha='center', fontsize=7, color='#c0392b')
ax.set_ylim(0, 150); ax.set_yticks([0, 20, 40, 60, 80])
ax2.set_ylim(-1.6, 1.45); ax2.set_yticks([0.8, 1.0, 1.2])
ax.set_ylabel('Committed TPS', y=0.27); ax2.set_ylabel('Finality (s)', color='#c0392b', y=0.80)
ax2.tick_params(axis='y', colors='#c0392b')
ax.set_xticks(range(N)); ax.set_xticklabels(labels, fontsize=7); ax.set_xlim(-0.6, N - 0.4)
for xb in (1.5, 4.5):
    ax.axvline(xb, color='#888888', lw=0.6, ls=':')
for x, txt in [(0.5, 'Endorsement'), (3, 'Block size'), (5.5, 'Organisations')]:
    ax.text(x, 92, txt, ha='center', va='center', fontsize=7, style='italic')
fig.tight_layout(pad=0.25)
os.makedirs(os.path.join(ROOT, 'figures'), exist_ok=True)
out = os.path.join(ROOT, 'figures', 'fig3_fabric.png')
fig.savefig(out, dpi=600)
print(out)
for r in rows:
    print(f"{r['label']}: {float(r['tps_committed']):.1f} TPS, finality {float(r['finality_mean_s']):.2f} s ({r['config']}, {r['run']})")
