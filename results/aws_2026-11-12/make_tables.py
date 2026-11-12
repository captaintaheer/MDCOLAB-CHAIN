#!/usr/bin/env python3
"""Build the summary tables of the AWS run of 12 Nov 2026 from the raw per-trial and per-transaction files.

Usage:  python make_tables.py [RUN_DIR]      (default: the directory of this script)
Reads   RUN_DIR/smpc_online/, RUN_DIR/pipeline/, RUN_DIR/fabric/
Writes  RUN_DIR/tables/*.csv and RUN_DIR/tables/tables.md
Needs   Python 3.10+ and NumPy.

Definitions
  online SMPC time   t_online_ms = t_eval_ms + t_recon_ms (layer-2/smpc_bench.py): from all input shares held
                     until await mpc.output(r) returns; secret sharing (t_sharing_ms) is reported separately.
  SMPC memory        peak RSS (ru_maxrss) of each party process; Table I uses the mean over parties.
  bytes per trial    bytes_sent_total / iterations of each party (warm-ups included in both).
  pipeline latency   t_pipeline_ms = sharing + eval + recon + hash + Fabric commit + read-back/verify
                     (harness/pipeline_bench.py); jobs/s = 1 / mean latency; memory = party-0 peak RSS.
  Fabric finality    CLI submit -> commit event at the Org1 peer for VALID transactions (harness/fabric_bench.py);
                     committed TPS = VALID commits / (last commit - first submit).
  95% CI             half-width t(0.975, N-1) * SD / sqrt(N).
"""
import csv, glob, json, os, re, sys
import numpy as np

ROOT = os.path.abspath(sys.argv[1] if len(sys.argv) > 1 else os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, 'tables')
os.makedirs(OUT, exist_ok=True)

T975 = [(1, 12.706), (2, 4.303), (3, 3.182), (4, 2.776), (5, 2.571), (6, 2.447), (7, 2.365), (8, 2.306), (9, 2.262),
        (10, 2.228), (14, 2.145), (19, 2.093), (29, 2.045), (49, 2.010), (99, 1.984)]


def t975(df):
    for k, q in T975:
        if df <= k:
            return q
    return 1.96


def rcsv(p):
    with open(p, newline='') as f:
        return list(csv.DictReader(f))


def col(rows, name, scale=1.0):
    return np.array([float(r[name]) for r in rows]) * scale


def stats(a):
    a = np.asarray(a, dtype=float)
    n = len(a)
    sd = float(a.std(ddof=1)) if n > 1 else float('nan')
    return dict(N=n, mean=float(a.mean()), sd=sd, ci95=t975(n - 1) * sd / np.sqrt(n) if n > 1 else float('nan'),
                median=float(np.median(a)), p95=float(np.percentile(a, 95)), p99=float(np.percentile(a, 99)),
                min=float(a.min()), max=float(a.max()))


def mems(d):
    return sorted((json.load(open(f)) for f in glob.glob(os.path.join(d, 'mem_*_p*.json'))), key=lambda m: m['pid'])


def write(name, rows, title, notes=()):
    if not rows:
        return
    keys = list(rows[0])
    for r in rows[1:]:
        keys += [k for k in r if k not in keys]
    with open(os.path.join(OUT, name + '.csv'), 'w', newline='') as f:
        w = csv.DictWriter(f, fieldnames=keys, lineterminator='\n')
        w.writeheader()
        w.writerows(rows)
    md = [f'## {title}', '', f'File: `tables/{name}.csv`', '', '| ' + ' | '.join(keys) + ' |', '|' + '---|' * len(keys)]
    for r in rows:
        md.append('| ' + ' | '.join(fmt(r.get(k, '')) for k in keys) + ' |')
    md += [''] + [f'* {n}' for n in notes] + ['']
    SECTIONS.append('\n'.join(md))


def fmt(x):
    if isinstance(x, float):
        return 'nan' if x != x else (f'{x:.4f}' if abs(x) < 10 else f'{x:.2f}')
    return str(x)


SECTIONS = []

# ---------------------------------------------------------------- online SMPC grid (Table I, AWS rows)
smpc = []
for d in sorted(glob.glob(os.path.join(ROOT, 'smpc_online', 'n*_k*')), key=lambda p: tuple(map(int, re.findall(r'\d+', os.path.basename(p))))):
    tr = glob.glob(os.path.join(d, 'trials_*.csv'))
    if not tr:
        continue
    T = rcsv(tr[0])
    M = mems(d)
    s = stats(col(T, 't_online_ms'))
    sent = [m['bytes_sent_total'] / m['iterations'] / 1e6 for m in M]
    smpc.append(dict(n=int(T[0]['n']), k=int(T[0]['k']), p_bits=int(T[0]['p_bits']), ssl=int(T[0]['ssl']), trials=s['N'],
                     online_mean_ms=s['mean'], online_sd_ms=s['sd'], online_ci95_ms=s['ci95'], online_median_ms=s['median'],
                     online_p95_ms=s['p95'], eval_mean_ms=float(col(T, 't_eval_ms').mean()),
                     recon_mean_ms=float(col(T, 't_recon_ms').mean()), sharing_mean_ms=float(col(T, 't_sharing_ms').mean()),
                     peak_rss_mean_mb=float(np.mean([m['peak_rss_mb'] for m in M])), peak_rss_max_mb=max(m['peak_rss_mb'] for m in M),
                     peak_rss_party0_mb=M[0]['peak_rss_mb'], parties_with_mem_file=len(M),
                     sent_per_party_per_trial_mean_mb=float(np.mean(sent)), sent_per_party_per_trial_max_mb=max(sent),
                     oracle_match=f"{sum(int(r['oracle_match']) for r in T)}/{len(T)}",
                     source=os.path.relpath(tr[0], ROOT)))
write('table1_smpc_online_grid', smpc, 'Online SMPC time and memory, one party per c6i.large node',
      ['MPyC 0.9 default field (64-bit prime), MPyC TLS off, t = (n-1)//2, 100 trials after 10 warm-ups, seed 20261017.',
       'Table I memory = peak_rss_mean_mb (mean of per-party peak RSS).'])

# ---------------------------------------------------------------- Fabric runs (Table II, Fig. 3)
fab = []
for sj in sorted(glob.glob(os.path.join(ROOT, 'fabric', 'bs*', '*', 'summary.json'))):
    s = json.load(open(sj))
    run_dir = os.path.dirname(sj)
    cfg, run = os.path.basename(os.path.dirname(run_dir)), os.path.basename(run_dir)
    txl = rcsv(os.path.join(run_dir, 'tx_log.csv'))
    fin = stats([float(t['finality_s']) for t in txl if t['status'] == 'VALID'])
    m = re.match(r'bs(\d+)_bt([\d.]+m?s)_endorse(\w+)_orgs(\d)', cfg)
    fab.append(dict(config=cfg, run=run, MaxMessageCount=int(m[1]), BatchTimeout=m[2], endorsement=m[3], orgs=int(m[4]),
                    endorsers_targeted=s['endorsers'], offered_rate_tps=s['rate_offered'] or 'sequential',
                    concurrency=s['concurrency'], submitted=s['submitted'], valid=s['valid'],
                    invalid_or_error=s['invalid_or_error'], window_s=s['window_s'], tps_committed=s['tps_committed'],
                    finality_mean_s=fin['mean'], finality_sd_s=fin['sd'], finality_median_s=fin['median'],
                    finality_p95_s=fin['p95'], finality_p99_s=fin['p99'], finality_min_s=fin['min'], finality_max_s=fin['max'],
                    source=os.path.relpath(run_dir, ROOT)))
write('table2_fabric_all_runs', fab, 'Fabric 2.5.4 runs, every configuration and offered load',
      ['One c6i.2xlarge running the Docker test-network: 1 etcdraft orderer, one peer per org, LevelDB, TLS.',
       'seq = 100 sequential transactions; rateR = open loop at R tx/s for 60 s; suffix _c64 = 64 client workers, otherwise 16.',
       'eN = number of endorsing peers targeted by each transaction.'])


def run(cfg, r):
    return next(x for x in fab if x['config'] == cfg and x['run'] == r)


def best(cfg, suffix):
    rs = [x for x in fab if x['config'] == cfg and x['run'].startswith('rate') and x['run'].endswith(suffix)]
    return max(rs, key=lambda x: x['tps_committed'])


B2, B02 = 'bs10_bt2s_endorseMAJORITY_orgs2', 'bs10_bt0.2s_endorseMAJORITY_orgs2'
t2 = [('Mean finality, lone transaction, BatchTimeout 0.2 s (s)', run(B02, 'seq_e2'), 'finality_mean_s'),
      ('Mean finality, lone transaction, BatchTimeout 2 s (s)', run(B2, 'seq_e2'), 'finality_mean_s'),
      ('Mean finality at 50 tx/s offered, BatchTimeout 0.2 s (s)', run(B02, 'rate50_e2'), 'finality_mean_s'),
      ('Committed throughput at 50 tx/s offered, BatchTimeout 0.2 s (TPS)', run(B02, 'rate50_e2'), 'tps_committed'),
      ('Committed throughput, 16 clients, BatchTimeout 0.2 s, max over offered loads (TPS)', best(B02, '_e2'), 'tps_committed'),
      ('Max committed throughput, majority, 2 orgs, 64 clients (TPS)', best(B2, '_c64'), 'tps_committed'),
      ('Max committed throughput, majority, 3 orgs, 64 clients (TPS)', best('bs10_bt2s_endorseMAJORITY_orgs3', '_e2_c64'), 'tps_committed'),
      ('Max committed throughput, 1-of-n endorsement, 2 orgs, 64 clients (TPS)', best('bs10_bt2s_endorseANY_orgs2', '_c64'), 'tps_committed')]
write('table2_fabric_summary', [dict(metric=m, value=r[k], config=r['config'], run=r['run'], submitted=r['submitted'],
                                     valid=r['valid'], finality_sd_s=r['finality_sd_s'], finality_p95_s=r['finality_p95_s'],
                                     finality_p99_s=r['finality_p99_s']) for m, r, k in t2],
      'Fabric summary (2 orgs, block size 10, majority unless stated)')
fig3 = [('Majority (baseline)', B2), ('1-of-n', 'bs10_bt2s_endorseANY_orgs2'), ('Block 10', B2),
        ('Block 30', 'bs30_bt2s_endorseMAJORITY_orgs2'), ('Block 50', 'bs50_bt2s_endorseMAJORITY_orgs2'),
        ('Orgs 2', B2), ('Orgs 3', 'bs10_bt2s_endorseMAJORITY_orgs3')]
write('fig3_values', [dict(label=l, config=c, run=r['run'], tps_committed=r['tps_committed'], finality_mean_s=r['finality_mean_s'])
                      for l, c in fig3 for r in [run(c, 'rate100_e1_c64' if 'ANY' in c else 'rate100_e2_c64')]],
      'Figure 3 values (offered 100 tx/s for 60 s, 64 clients, BatchTimeout 2 s)')

# ---------------------------------------------------------------- pipeline (Table III, Table V, stage breakdown)
def pipe_rows(cfg):
    out = []
    dirs = glob.glob(os.path.join(ROOT, 'pipeline', cfg, 'n*_k*'))
    for d in sorted(dirs, key=lambda p: tuple(map(int, re.findall(r'\d+', os.path.basename(p))))):
        tr = glob.glob(os.path.join(d, 'trials_*.csv'))
        if not tr:
            continue
        T = rcsv(tr[0])
        M = mems(d)
        L = stats(col(T, 't_pipeline_ms', 1e-3))
        out.append(dict(config=cfg, n=int(T[0]['n']), t=int(T[0]['t']), k=int(T[0]['k']), trials=L['N'],
                        latency_mean_s=L['mean'], latency_sd_s=L['sd'], latency_ci95_s=L['ci95'], latency_median_s=L['median'],
                        latency_p95_s=L['p95'], jobs_per_s=1 / L['mean'],
                        sharing_mean_ms=float(col(T, 't_sharing_ms').mean()), eval_mean_ms=float(col(T, 't_eval_ms').mean()),
                        recon_mean_ms=float(col(T, 't_recon_ms').mean()), online_mean_ms=float(col(T, 't_online_ms').mean()),
                        hash_mean_ms=float(col(T, 't_hash_ms').mean()), commit_mean_ms=float(col(T, 't_fabric_commit_ms').mean()),
                        readback_verify_mean_ms=float(col(T, 't_readback_verify_ms').mean()),
                        plain_numpy_mean_ms=float(col(T, 't_plain_numpy_ms').mean()),
                        peak_rss_party0_mb=M[0]['peak_rss_mb'] if M and M[0]['pid'] == 0 else float('nan'),
                        peak_rss_max_other_parties_mb=max((m['peak_rss_mb'] for m in M if m['pid'] != 0), default=float('nan')),
                        sent_per_party_per_trial_mean_mb=float(np.mean([m['bytes_sent_total'] / m['iterations'] / 1e6 for m in M])),
                        oracle_match=f"{sum(int(r['oracle_match']) for r in T)}/{len(T)}",
                        fabric_ok=f"{sum(r['fabric_ok'] == 'True' for r in T)}/{len(T)}",
                        readback_verified=f"{sum(r['readback_verified'] == 'True' for r in T)}/{len(T)}",
                        source=os.path.relpath(tr[0], ROOT)))
    return out


P02, P2 = pipe_rows(B02), pipe_rows(B2)
note_p = ['Party 0 on the Fabric node (c6i.2xlarge), parties 1..n-1 one per c6i.large node; 100 trials after 10 warm-ups.',
          'latency = sharing + eval + recon + hash + commit + read-back/verify; memory column for Table III = peak_rss_party0_mb.']
write('table3_pipeline_bt0p2s', P02, 'Pipeline, BatchTimeout 0.2 s (Table III main values)', note_p)
write('table3_pipeline_bt2s', P2, 'Pipeline, BatchTimeout 2 s (Table III values in parentheses; Table V)', note_p)
t5 = [dict(group='parties', **{k: r[k] for k in ('n', 't', 'k', 'latency_mean_s', 'peak_rss_party0_mb', 'oracle_match', 'source')})
      for r in P2 if r['k'] == 10000 and r['t'] == (r['n'] - 1) // 2 and '_t' not in os.path.basename(os.path.dirname(r['source']))]
t5 += [dict(group='threshold', **{k: r[k] for k in ('n', 't', 'k', 'latency_mean_s', 'peak_rss_party0_mb', 'oracle_match', 'source')})
       for r in P2 if os.path.basename(os.path.dirname(r['source'])).startswith('n8_k10000_t')]
write('table5_components', t5, 'Component analysis, k = 10 000, BatchTimeout 2 s (Table V)',
      ['threshold rows use pipeline_bench.py -T t with n = 8.'])

# ---------------------------------------------------------------- inter-node RTT (ICMP, 20 pings per ordered pair)
ss, sf = [], []
for line in open(os.path.join(ROOT, 'env', 'rtt_ping_fullmesh.txt')):
    m = re.match(r'\[(\d+)\] <([\w-]+)> rtt min/avg/max/mdev = ([\d.]+)/([\d.]+)/([\d.]+)/([\d.]+) ms', line)
    if not m:
        continue
    if m[2] == 'fabric-node':
        sf.append(float(m[4]))
    elif m[2] != f'smpc-node{int(m[1]):02d}':  # skip a node pinging itself
        ss.append(float(m[4]))
write('rtt_summary', [dict(path=p, pairs=len(a), mean_of_pair_avg_ms=float(np.mean(a)), median_ms=float(np.median(a)),
                           min_pair_avg_ms=min(a), max_pair_avg_ms=max(a))
                      for p, a in [('smpc_to_smpc', ss), ('smpc_to_fabric_node', sf)]],
      'Inter-node round-trip time (ICMP)', ['Source: env/rtt_ping_fullmesh.txt; one line per ordered pair (20 pings).'])

# ---------------------------------------------------------------- correctness totals
allp = P02 + P2
tot = dict(smpc_trials=sum(r['trials'] for r in smpc), smpc_oracle_match=sum(int(r['oracle_match'].split('/')[0]) for r in smpc),
           pipeline_trials=sum(r['trials'] for r in allp), pipeline_oracle_match=sum(int(r['oracle_match'].split('/')[0]) for r in allp),
           pipeline_fabric_ok=sum(int(r['fabric_ok'].split('/')[0]) for r in allp),
           pipeline_readback_verified=sum(int(r['readback_verified'].split('/')[0]) for r in allp),
           fabric_transactions=sum(r['submitted'] for r in fab), fabric_valid=sum(r['valid'] for r in fab))
write('correctness_totals', [tot], 'Correctness totals over all AWS runs')

with open(os.path.join(OUT, 'tables.md'), 'w') as f:
    f.write('# Tables of the AWS run of 12 Nov 2026\n\nBuilt by make_tables.py from the raw files of this folder.\n\n')
    f.write('\n'.join(SECTIONS))
print(f'wrote {len(SECTIONS)} tables to {OUT}')
