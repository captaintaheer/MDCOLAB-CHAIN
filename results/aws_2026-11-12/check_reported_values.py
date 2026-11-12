#!/usr/bin/env python3
"""Compare the values reported for the AWS evaluation with the tables built by make_tables.py.

Usage:  python make_tables.py && python check_reported_values.py [RUN_DIR]
Each reported value is compared with the computed value rounded to the same number of decimals.
Exit status 0 if every value matches, 1 otherwise.
"""
import csv, os, sys

ROOT = os.path.abspath(sys.argv[1] if len(sys.argv) > 1 else os.path.dirname(os.path.abspath(__file__)))
T = lambda name: list(csv.DictReader(open(os.path.join(ROOT, 'tables', name + '.csv'))))
smpc = {(int(r['n']), int(r['k'])): r for r in T('table1_smpc_online_grid')}
p02 = {(int(r['n']), int(r['k'])): r for r in T('table3_pipeline_bt0p2s')}
p2 = {(int(r['n']), int(r['k'])): r for r in T('table3_pipeline_bt2s') if not os.path.dirname(r['source']).split('/')[-1].count('_t')}
p2t = {int(r['t']): r for r in T('table3_pipeline_bt2s') if '_t' in os.path.dirname(r['source']).split('/')[-1]}
fab = {r['metric']: r for r in T('table2_fabric_summary')}
fall = {(r['config'], r['run']): r for r in T('table2_fabric_all_runs')}
tot = T('correctness_totals')[0]
checks = []


def chk(label, reported, computed, decimals):
    checks.append((label, reported, round(float(computed), decimals), round(float(computed), decimals) == reported))


# Table I, AWS rows: online time (ms) / mean per-party peak RSS (MB)
for (n, k), (ms, mb) in {(4, 10000): (8.37, 47.14), (4, 50000): (42.21, 72.73), (8, 10000): (13.47, 54.41),
                         (8, 50000): (65.01, 108.25), (12, 10000): (20.30, 61.28), (12, 50000): (110.04, 139.83),
                         (16, 10000): (37.18, 69.20), (16, 50000): (175.13, 172.92)}.items():
    chk(f'Table I n={n} k={k} online ms', ms, smpc[n, k]['online_mean_ms'], 2)
    chk(f'Table I n={n} k={k} memory MB', mb, smpc[n, k]['peak_rss_mean_mb'], 2)
chk('Table I footnote min SD ms', 0.50, min(float(r['online_sd_ms']) for r in smpc.values()), 2)
chk('Table I footnote max SD ms', 18.30, max(float(r['online_sd_ms']) for r in smpc.values()), 2)
chk('Table I footnote max 95% CI ms', 3.6, max(float(r['online_ci95_ms']) for r in smpc.values()), 1)

# Table II
for metric, v, d in [('Mean finality, lone transaction, BatchTimeout 0.2 s (s)', 0.28, 2),
                     ('Mean finality, lone transaction, BatchTimeout 2 s (s)', 2.08, 2),
                     ('Mean finality at 50 tx/s offered, BatchTimeout 0.2 s (s)', 0.21, 2),
                     ('Committed throughput at 50 tx/s offered, BatchTimeout 0.2 s (TPS)', 49.8, 1),
                     ('Committed throughput, 16 clients, BatchTimeout 0.2 s, max over offered loads (TPS)', 56.7, 1),
                     ('Max committed throughput, majority, 2 orgs, 64 clients (TPS)', 61.5, 1),
                     ('Max committed throughput, majority, 3 orgs, 64 clients (TPS)', 60.1, 1),
                     ('Max committed throughput, 1-of-n endorsement, 2 orgs, 64 clients (TPS)', 72.1, 1)]:
    chk('Table II ' + metric, v, fab[metric]['value'], d)
chk('Table II footnote finality SD, lone tx BT 0.2 s', 0.002, fab['Mean finality, lone transaction, BatchTimeout 0.2 s (s)']['finality_sd_s'], 3)
chk('Table II footnote finality SD, 50 tx/s BT 0.2 s', 0.058, fab['Mean finality at 50 tx/s offered, BatchTimeout 0.2 s (s)']['finality_sd_s'], 3)
chk('Table II footnote p95, lone tx BT 0.2 s', 0.28, fab['Mean finality, lone transaction, BatchTimeout 0.2 s (s)']['finality_p95_s'], 2)
chk('Table II footnote p95, 50 tx/s BT 0.2 s', 0.30, fab['Mean finality at 50 tx/s offered, BatchTimeout 0.2 s (s)']['finality_p95_s'], 2)
chk('Table II footnote p99, lone tx BT 0.2 s', 0.28, fab['Mean finality, lone transaction, BatchTimeout 0.2 s (s)']['finality_p99_s'], 2)
chk('Table II footnote p99, 50 tx/s BT 0.2 s', 0.31, fab['Mean finality at 50 tx/s offered, BatchTimeout 0.2 s (s)']['finality_p99_s'], 2)
f3 = T('fig3_values')
chk('Figure 3 min finality s', 0.88, min(float(r['finality_mean_s']) for r in f3), 2)
chk('Figure 3 max finality s', 1.08, max(float(r['finality_mean_s']) for r in f3), 2)

# Table III: latency BT 0.2 s (BT 2 s), jobs/s, party-0 peak memory
for (n, k), (l02, l2, j, mb) in {(4, 10000): (0.36, 2.16, 2.76, 48.9), (4, 50000): (0.52, 2.33, 1.91, 76.2),
                                 (4, 100000): (0.72, 2.53, 1.38, 110.7), (8, 10000): (0.42, 2.23, 2.36, 56.6),
                                 (8, 50000): (0.84, 2.64, 1.19, 113.0), (8, 100000): (1.36, 3.16, 0.74, 187.8),
                                 (12, 10000): (0.49, 2.30, 2.02, 63.5), (12, 50000): (1.19, 2.99, 0.84, 147.4),
                                 (16, 10000): (0.58, 2.38, 1.74, 71.9), (16, 50000): (1.58, 3.39, 0.63, 182.2)}.items():
    chk(f'Table III n={n} k={k} latency s (BT 0.2 s)', l02, p02[n, k]['latency_mean_s'], 2)
    chk(f'Table III n={n} k={k} latency s (BT 2 s)', l2, p2[n, k]['latency_mean_s'], 2)
    chk(f'Table III n={n} k={k} jobs/s', j, p02[n, k]['jobs_per_s'], 2)
    chk(f'Table III n={n} k={k} memory MB', mb, p02[n, k]['peak_rss_party0_mb'], 1)
allp = list(p02.values()) + list(T('table3_pipeline_bt2s'))
chk('Table III footnote max latency SD s', 0.014, max(float(r['latency_sd_s']) for r in allp), 3)
chk('Table III footnote commit s (BT 0.2 s)', 0.28, max(float(r['commit_mean_ms']) for r in p02.values()) / 1e3, 2)
chk('Table III footnote commit s (BT 2 s)', 2.08, max(float(r['commit_mean_ms']) for r in p2.values()) / 1e3, 2)
chk('Table III footnote read-back s', 0.04, max(float(r['readback_verify_mean_ms']) for r in p02.values()) / 1e3, 2)
chk('Table III footnote min sharing ms', 30, min(float(r['sharing_mean_ms']) for r in p02.values()), 0)
chk('Table III footnote max sharing ms', 1105, max(float(r['sharing_mean_ms']) for r in p02.values()), 0)
chk('Table III footnote min online ms', 8, min(float(r['online_mean_ms']) for r in p02.values()), 0)
chk('Table III footnote max online ms', 162, max(float(r['online_mean_ms']) for r in p02.values()), 0)

# Stage breakdown n=8, k=10 000, BT 0.2 s
s = p02[8, 10000]
for lab, v, key, scale, d in [('sharing ms', 86.4, 'sharing_mean_ms', 1, 1), ('online ms', 13.9, 'online_mean_ms', 1, 1),
                              ('hash ms', 0.1, 'hash_mean_ms', 1, 1), ('commit s', 0.28, 'commit_mean_ms', 1e-3, 2),
                              ('read-back ms', 44.3, 'readback_verify_mean_ms', 1, 1), ('total s', 0.42, 'latency_mean_s', 1, 2)]:
    chk('Stage breakdown n=8 k=10000 ' + lab, v, float(s[key]) * scale, d)

# Table V (BT 2 s): latency s / party-0 memory MB
for n, (l, mb) in {4: (2.16, 48.6), 8: (2.23, 56.6), 12: (2.30, 63.2), 16: (2.38, 72.1)}.items():
    chk(f'Table V parties n={n} latency s', l, p2[n, 10000]['latency_mean_s'], 2)
    chk(f'Table V parties n={n} memory MB', mb, p2[n, 10000]['peak_rss_party0_mb'], 1)
for t, (l, mb) in {1: (2.18, 54.0), 2: (2.20, 55.6), 3: (2.23, 56.5)}.items():
    chk(f'Table V threshold t={t} latency s', l, p2t[t]['latency_mean_s'], 2)
    chk(f'Table V threshold t={t} memory MB', mb, p2t[t]['peak_rss_party0_mb'], 1)
chk('Table V baseline NumPy ms (n=8, k=10000, BT 0.2 s)', 0.30, s['plain_numpy_mean_ms'], 2)
chk('Table V baseline MPyC without ledger ms (sharing + online)', 100, float(s['sharing_mean_ms']) + float(s['online_mean_ms']), 0)

# Communication and correctness
chk('Bytes sent per party per trial, min MB', 0.40, min(float(r['sent_per_party_per_trial_mean_mb']) for r in smpc.values()), 2)
chk('Bytes sent per party per trial, max MB', 11.0, max(float(r['sent_per_party_per_trial_mean_mb']) for r in smpc.values()), 1)
chk('Bytes sent per party per trial, n=8 k=10000 MB', 1.00, smpc[8, 10000]['sent_per_party_per_trial_mean_mb'], 2)
chk('Correctness trials (SMPC + pipeline)', 3100, int(tot['smpc_trials']) + int(tot['pipeline_trials']), 0)
chk('Correctness oracle matches', 3100, int(tot['smpc_oracle_match']) + int(tot['pipeline_oracle_match']), 0)
chk('Pipeline read-back verified', 2300, tot['pipeline_readback_verified'], 0)

rtt = {r['path']: r for r in T('rtt_summary')}
chk('RTT SMPC to SMPC mean ms', 0.15, rtt['smpc_to_smpc']['mean_of_pair_avg_ms'], 2)
chk('RTT SMPC to Fabric node mean ms', 0.244, rtt['smpc_to_fabric_node']['mean_of_pair_avg_ms'], 3)

bad = [c for c in checks if not c[3]]
for label, rep, comp, ok in checks:
    print(f"{'OK ' if ok else 'DIFF'} {label}: reported {rep}, computed {comp}")
print(f'{len(checks) - len(bad)}/{len(checks)} values match')
sys.exit(1 if bad else 0)
