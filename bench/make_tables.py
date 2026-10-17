#!/usr/bin/env python3
"""Print markdown tables from results/*.csv (no numbers are typed by hand)."""
import csv, os, sys, numpy as np
root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
R = lambda f: list(csv.DictReader(open(os.path.join(root, 'results', f)))) if os.path.exists(os.path.join(root, 'results', f)) else []
f2 = lambda x, d=2: f"{float(x):.{d}f}"
for prof in ['aligned', 'default']:
    S = R(f'smpc_summary_{prof}.csv')
    if not S: continue
    print(f"\n#### Online SMPC time and memory, profile `{prof}` (p = {S[0]['p_bits']}-bit, TLS = {'on' if S[0]['ssl']=='1' else 'off'}; N = {S[0]['N']} after 10 warm-ups)\n")
    print("| n | k | online mean ± SD (ms) | median | p95 | p99 | peak RSS party 0 (MB) | peak RSS max over parties (MB) | bytes sent / party / iter | oracle match |")
    print("|---|---|---|---|---|---|---|---|---|---|")
    for s in S:
        print(f"| {s['n']} | {s['k']} | {f2(s['t_online_ms_mean'])} ± {f2(s['t_online_ms_sd'])} | {f2(s['t_online_ms_median'])} | {f2(s['t_online_ms_p95'])} | {f2(s['t_online_ms_p99'])} | {f2(s['peak_rss_mb_party0'],1)} | {f2(s['peak_rss_mb_max'],1)} | {float(s['bytes_sent_per_party_per_iter_mean'])/1e6:.2f} MB | {s['oracle_match']}/{s['N']} |")
    print(f"\n#### Per-stage means ± SD (ms), profile `{prof}` (Fabric stage not measurable here)\n")
    print("| n | k | share gen + distribution | online eval | reconstruction | online (eval+recon) | SHA-256 commit | verification | total measured (sharing→verify) |")
    print("|---|---|---|---|---|---|---|---|---|")
    for s in S:
        c = lambda st: f"{f2(s[st+'_mean'])} ± {f2(s[st+'_sd'])}"
        print(f"| {s['n']} | {s['k']} | {c('t_sharing_ms')} | {c('t_eval_ms')} | {c('t_recon_ms')} | {c('t_online_ms')} | {c('t_hash_ms')} | {c('t_verify_ms')} | {c('t_total_smpc_ms')} |")
O = R('original_layer2_smpc.csv')
if O:
    print("\n#### Unmodified `layer2_smpc.py` (3 public scalars, timer = mpc.start()..mpc.shutdown(), num_ops=5), 20 runs per m\n")
    print("| parties m | Execution Time mean ± SD (ms) | median | p95 | Peak RAM mean (MB) | Comm bytes | results |")
    print("|---|---|---|---|---|---|---|")
    for m in sorted({int(o['parties']) for o in O}):
        X = [o for o in O if int(o['parties']) == m and o['execution_time_s']]
        t = np.array([float(o['execution_time_s']) for o in X]) * 1e3
        r = np.array([float(o['peak_ram_mb']) for o in X])
        print(f"| {m} | {t.mean():.1f} ± {t.std(ddof=1):.1f} | {np.median(t):.1f} | {np.percentile(t,95):.1f} | {r.mean():.2f} | {X[0]['comm_bytes']} | {X[0]['results']} |")
P = R('preagg_synthetic.csv')
if P:
    print("\n#### Synthetic pre-aggregation (party 0: 2504/n samples x k dosage matrix -> column sums), 25 reps\n")
    print("| n | k | samples (party 0) | mean ± SD (ms) | median | p95 |")
    print("|---|---|---|---|---|---|")
    for p in P:
        print(f"| {p['n']} | {p['k']} | {p['samples_party0']} | {f2(p['preagg_mean_ms'])} ± {f2(p['preagg_sd_ms'])} | {f2(p['preagg_median_ms'])} | {f2(p['preagg_p95_ms'])} |")
