#!/usr/bin/env python3
"""Fabric ledger load harness (added November 2026; used for the AWS run of 12 Nov 2026).

Submits CreateAsset transactions (asset-transfer-basic) with the Fabric peer CLI, like automate_layers.py,
but always with --waitForEvent so each transaction's finality (CLI submit -> commit event at the Org1 peer)
is observed, and logs every transaction to tx_log.csv.
  --rate 0          closed loop, one client, sequential transactions (low-load finality)
  --rate R > 0      open loop: transaction i is scheduled at t0 + i/R, executed by up to --concurrency
                    client workers; if all workers are busy the transaction starts late (lag is logged)
TPS (committed) = VALID commits / (last commit time - first submit time).
Finality includes peer-CLI process start-up, gRPC/TLS connection set-up, endorsement, ordering
(BatchTimeout / MaxMessageCount), validation and commit.
A background thread samples `docker stats` (per-container CPU and memory) and host CPU into resources.csv.
"""
import argparse, csv, json, os, re, subprocess, threading, time, datetime, zoneinfo
import psutil
KL = zoneinfo.ZoneInfo('Asia/Kuala_Lumpur')
ap = argparse.ArgumentParser()
ap.add_argument('--rate', type=float, default=0); ap.add_argument('--duration', type=float, default=60)
ap.add_argument('--txs', type=int, default=None, help='closed loop: number of transactions')
ap.add_argument('--concurrency', type=int, default=16); ap.add_argument('--endorsers', type=int, default=2)
ap.add_argument('--out-dir', required=True); ap.add_argument('--tag', default='run')
ap.add_argument('--sample-s', type=float, default=2.0)
a = ap.parse_args()
TN = os.environ['FABRIC_TEST_NETWORK']
ORG = lambda i, p: f'{TN}/organizations/peerOrganizations/org{i}.example.com/peers/peer0.org{i}.example.com/tls/ca.crt'
PORT = {1: 7051, 2: 9051, 3: 11051}
OCA = f'{TN}/organizations/ordererOrganizations/example.com/orderers/orderer.example.com/msp/tlscacerts/tlsca.example.com-cert.pem'
env = dict(os.environ, FABRIC_CFG_PATH=f'{TN}/../config', CORE_PEER_TLS_ENABLED='true', CORE_PEER_LOCALMSPID='Org1MSP',
           CORE_PEER_TLS_ROOTCERT_FILE=ORG(1, 0), CORE_PEER_ADDRESS='localhost:7051',
           CORE_PEER_MSPCONFIGPATH=f'{TN}/organizations/peerOrganizations/org1.example.com/users/Admin@org1.example.com/msp')
peer = f'{TN}/../bin/peer'
os.makedirs(a.out_dir, exist_ok=True)
run_id = f'{a.tag}_{int(time.time())}'
digest = '50f72405baf11b0f73f6a3db7152798bf2f958384e806befdf4ee6ddfdd9e198'  # layer-2/output/result_hash.txt of the reference run

def invoke(i):
    args = [peer, 'chaincode', 'invoke', '-o', 'localhost:7050', '--ordererTLSHostnameOverride', 'orderer.example.com',
            '--tls', '--cafile', OCA, '-C', 'mychannel', '-n', 'basic']
    for o in range(1, a.endorsers + 1):
        args += ['--peerAddresses', f'localhost:{PORT[o]}', '--tlsRootCertFiles', ORG(o, 0)]
    args += ['--waitForEvent', '-c', json.dumps({'function': 'CreateAsset', 'Args': [f'{run_id}_{i}', digest, '0', 'mdcolab', '0']})]
    t0 = time.time(); p = subprocess.run(args, env=env, capture_output=True, text=True); t1 = time.time()
    m = re.search(r'txid \[([0-9a-f]+)\] committed with status \((\w+)\)', p.stderr)
    status = m.group(2) if m else ('ERROR' if p.returncode else 'UNKNOWN')
    err = '' if m and status == 'VALID' else (p.stderr.strip().splitlines() or [''])[-1][-240:]
    return dict(tx=i, txid=m.group(1) if m else '', submit_ts=t0, commit_ts=t1, finality_s=t1 - t0, rc=p.returncode,
                status=status, error=err)

res_rows, stop = [], threading.Event()
def sampler():
    while not stop.is_set():
        ts = time.time(); host_cpu = psutil.cpu_percent(interval=None)
        try:
            out = subprocess.run(['docker', 'stats', '--no-stream', '--format', '{{.Name}}\t{{.CPUPerc}}\t{{.MemUsage}}'],
                                 capture_output=True, text=True, timeout=20).stdout
        except Exception:
            out = ''
        for line in out.splitlines():
            n, c, mu = (line.split('\t') + ['', '', ''])[:3]
            res_rows.append(dict(ts=ts, container=n, cpu_pct=c.rstrip('%'), mem_usage=mu.split('/')[0].strip(),
                                 host_cpu_pct=host_cpu, host_mem_avail_mb=psutil.virtual_memory().available / 2**20))
        stop.wait(a.sample_s)
psutil.cpu_percent(interval=None)
th = threading.Thread(target=sampler, daemon=True); th.start()
rows, lock = [], threading.Lock()
start_wall = datetime.datetime.now(KL)
if a.rate <= 0:
    n = a.txs or 100
    for i in range(n):
        r = invoke(i); r['scheduled_ts'] = r['submit_ts']; rows.append(r)
else:
    n = int(round(a.rate * a.duration)); t_start = time.time() + 0.5; nxt = [0]
    def worker():
        while True:
            with lock:
                i = nxt[0]; nxt[0] += 1
            if i >= n:
                return
            sched = t_start + i / a.rate
            d = sched - time.time()
            if d > 0:
                time.sleep(d)
            r = invoke(i); r['scheduled_ts'] = sched
            with lock:
                rows.append(r)
    ws = [threading.Thread(target=worker) for _ in range(a.concurrency)]
    [w.start() for w in ws]; [w.join() for w in ws]
stop.set(); th.join(timeout=30)
rows.sort(key=lambda r: r['tx'])
with open(os.path.join(a.out_dir, 'tx_log.csv'), 'w', newline='') as f:
    w = csv.DictWriter(f, fieldnames=['tx', 'txid', 'scheduled_ts', 'submit_ts', 'commit_ts', 'finality_s', 'rc', 'status', 'error'])
    w.writeheader(); w.writerows(rows)
if res_rows:
    with open(os.path.join(a.out_dir, 'resources.csv'), 'w', newline='') as f:
        w = csv.DictWriter(f, fieldnames=list(res_rows[0])); w.writeheader(); w.writerows(res_rows)
valid = [r for r in rows if r['status'] == 'VALID']
span = (max(r['commit_ts'] for r in rows) - min(r['submit_ts'] for r in rows)) if rows else 0
fin = sorted(r['finality_s'] for r in valid)
summ = dict(tag=a.tag, rate_offered=a.rate, duration_s=a.duration if a.rate > 0 else None, concurrency=a.concurrency if a.rate > 0 else 1,
            endorsers=a.endorsers, submitted=len(rows), valid=len(valid),
            invalid_or_error=len(rows) - len(valid), window_s=span, tps_committed=len(valid) / span if span else 0,
            submit_rate_achieved=(len(rows) - 1) / (max(r['submit_ts'] for r in rows) - min(r['submit_ts'] for r in rows)) if len(rows) > 1 else 0,
            finality_mean_s=sum(fin) / len(fin) if fin else None,
            finality_median_s=fin[len(fin) // 2] if fin else None,
            finality_p95_s=fin[int(0.95 * (len(fin) - 1))] if fin else None,
            start=start_wall.isoformat(timespec='seconds'), statuses={s: sum(1 for r in rows if r['status'] == s) for s in {r['status'] for r in rows}})
json.dump(summ, open(os.path.join(a.out_dir, 'summary.json'), 'w'), indent=1)
print(json.dumps(summ))
