#!/usr/bin/env python3
"""Summarise per-trial CSVs into results/smpc_summary_<profile>.csv (mean, SD, median, p95, p99 per stage)."""
import csv, os, sys, numpy as np
root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
stages = ['t_sharing_ms', 't_eval_ms', 't_recon_ms', 't_online_ms', 't_hash_ms', 't_verify_ms', 't_total_smpc_ms']
for prof in sys.argv[1:] or ['aligned', 'default']:
    f = os.path.join(root, 'results', f'smpc_trials_{prof}.csv')
    if not os.path.exists(f):
        continue
    T = list(csv.DictReader(open(f)))
    M = list(csv.DictReader(open(os.path.join(root, 'results', f'smpc_memory_{prof}.csv'))))
    out = []
    for key in sorted({(int(r['n']), int(r['k'])) for r in T}, key=lambda x: (x[1], x[0])):
        R = [r for r in T if (int(r['n']), int(r['k'])) == key]
        mem = [float(m['peak_rss_mb']) for m in M if (int(m['n']), int(m['k'])) == key]
        byt = [int(m['bytes_sent_total']) / int(m['iterations']) for m in M if (int(m['n']), int(m['k'])) == key]
        row = {'profile': prof, 'n': key[0], 'k': key[1], 'p_bits': R[0]['p_bits'], 'ssl': R[0]['ssl'], 'N': len(R),
               'oracle_match': sum(int(r['oracle_match']) for r in R)}
        for s in stages:
            a = np.array([float(r[s]) for r in R])
            row.update({f'{s}_mean': a.mean(), f'{s}_sd': a.std(ddof=1), f'{s}_median': np.median(a),
                        f'{s}_p95': np.percentile(a, 95), f'{s}_p99': np.percentile(a, 99)})
        row.update({'peak_rss_mb_party0': mem[0] if mem else '', 'peak_rss_mb_max': max(mem), 'peak_rss_mb_mean': np.mean(mem),
                    'bytes_sent_per_party_per_iter_mean': np.mean(byt)})
        out.append(row)
    with open(os.path.join(root, 'results', f'smpc_summary_{prof}.csv'), 'w', newline='') as g:
        w = csv.DictWriter(g, fieldnames=list(out[0])); w.writeheader(); w.writerows(out)
    for r in out:
        print(f"{prof} n={r['n']:>2} k={r['k']:>6}  online {r['t_online_ms_mean']:.2f}±{r['t_online_ms_sd']:.2f} med {r['t_online_ms_median']:.2f} p95 {r['t_online_ms_p95']:.2f} | share {r['t_sharing_ms_mean']:.1f} eval {r['t_eval_ms_mean']:.2f} recon {r['t_recon_ms_mean']:.2f} hash {r['t_hash_ms_mean']:.2f} | total {r['t_total_smpc_ms_mean']:.1f} | RSS p0 {r['peak_rss_mb_party0']:.1f} max {r['peak_rss_mb_max']:.1f} | match {r['oracle_match']}/{r['N']}")
