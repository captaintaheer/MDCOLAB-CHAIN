#!/usr/bin/env python3
"""MDCOLAB-CHAIN cryptographic-and-ledger pipeline harness (added November 2026; used for the AWS run of 12 Nov 2026).

It re-uses the SMPC code path of layer-2/smpc_bench.py
(same synthetic generator, per-sender mpc.input, same timers) and adds, on party 0:
  * SHA-256 commitment h = SHA-256(enc(r) || enc(meta))  (enc as in smpc_bench.py),
  * a Fabric commit of h with the peer CLI (CreateAsset on the 'basic' chaincode, --waitForEvent, so the
    timer stops when the Org1 peer reports the transaction committed),
  * a ReadAsset read-back and digest comparison (consumer-side verification),
  * an independent NumPy plaintext oracle and its timing (plaintext baseline),
  * MPyC protocol bytes sent per party, peak RSS per party.
Pipeline latency (t_pipeline_ms) = sharing + online (eval+recon) + hash + Fabric commit + read-back/verify,
i.e. from 'pre-aggregated vectors in memory' to 'verified result'. Process start-up and MPyC connection
set-up are excluded.

--preagg off (ablation): each party secret-shares its per-sample genotype matrix (n_i x k, values 0/1/2)
instead of its allele-count vector; the parties compute the same aggregate r (sum over samples and parties).
To bound memory, the matrix is shared and summed in column chunks of --chunk SNPs within one trial.

Usage (all parties local processes):
  python pipeline_bench.py -M 8 --k 10000 --trials 100 --warmup 10 --fabric --out-dir DIR --tag TAG [-T t] [--preagg off]
"""
import argparse, csv, hashlib, json, os, resource, struct, subprocess, sys, time
import numpy as np
from mpyc.runtime import mpc

N_SAMPLES = 2504
ap = argparse.ArgumentParser()
ap.add_argument('--k', type=int, default=10000)
ap.add_argument('--trials', type=int, default=100)
ap.add_argument('--warmup', type=int, default=10)
ap.add_argument('--bits', type=int, default=None)
ap.add_argument('--seed', type=int, default=20261017)
ap.add_argument('--fabric', action='store_true')
ap.add_argument('--preagg', choices=['on', 'off'], default='on')
ap.add_argument('--chunk', type=int, default=500)
ap.add_argument('--out-dir', default='out')
ap.add_argument('--tag', default='run')
args, _ = ap.parse_known_args()

TN = os.environ.get('FABRIC_TEST_NETWORK', '')


def party_samples(pid, m):
    return sum(1 for s in range(N_SAMPLES) if s % m == pid)


def af_vec(trial, k):
    return np.random.default_rng([args.seed, trial + 1000, 10**6]).uniform(0.01, 0.5, k)


def party_vector(trial, pid, m, k):          # identical to layer-2/smpc_bench.py
    af = af_vec(trial, k)
    rng = np.random.default_rng([args.seed, trial + 1000, pid])
    return rng.binomial(2 * party_samples(pid, m), af).astype(np.int64)


def party_genotypes(trial, pid, m, k):       # pre-aggregation OFF: per-sample genotypes 0/1/2
    af = af_vec(trial, k)
    rng = np.random.default_rng([args.seed, trial + 1000, pid, 7])
    return rng.binomial(2, af, size=(party_samples(pid, m), k)).astype(np.int64)


def enc_vec(r):
    r = np.asarray(r, dtype='<u8')
    return struct.pack('<Q', r.size) + r.tobytes()


def fabric_env():
    o1 = f'{TN}/organizations/peerOrganizations/org1.example.com/peers/peer0.org1.example.com/tls/ca.crt'
    return dict(os.environ, FABRIC_CFG_PATH=f'{TN}/../config', CORE_PEER_TLS_ENABLED='true',
                CORE_PEER_LOCALMSPID='Org1MSP', CORE_PEER_TLS_ROOTCERT_FILE=o1,
                CORE_PEER_MSPCONFIGPATH=f'{TN}/organizations/peerOrganizations/org1.example.com/users/Admin@org1.example.com/msp',
                CORE_PEER_ADDRESS='localhost:7051')


def fabric_commit(h_hex, asset_id):
    peer = f'{TN}/../bin/peer'
    o1 = f'{TN}/organizations/peerOrganizations/org1.example.com/peers/peer0.org1.example.com/tls/ca.crt'
    o2 = f'{TN}/organizations/peerOrganizations/org2.example.com/peers/peer0.org2.example.com/tls/ca.crt'
    oca = f'{TN}/organizations/ordererOrganizations/example.com/orderers/orderer.example.com/msp/tlscacerts/tlsca.example.com-cert.pem'
    env = fabric_env()
    inv = [peer, 'chaincode', 'invoke', '-o', 'localhost:7050', '--ordererTLSHostnameOverride', 'orderer.example.com',
           '--tls', '--cafile', oca, '-C', 'mychannel', '-n', 'basic',
           '--peerAddresses', 'localhost:7051', '--tlsRootCertFiles', o1,
           '--peerAddresses', 'localhost:9051', '--tlsRootCertFiles', o2, '--waitForEvent',
           '-c', json.dumps({'function': 'CreateAsset', 'Args': [asset_id, h_hex, '0', 'mdcolab', '0']})]
    t0 = time.perf_counter(); p = subprocess.run(inv, env=env, capture_output=True, text=True); t1 = time.perf_counter()
    ok = p.returncode == 0 and 'committed with status (VALID)' in p.stderr
    q = [peer, 'chaincode', 'query', '-C', 'mychannel', '-n', 'basic', '-c',
         json.dumps({'function': 'ReadAsset', 'Args': [asset_id]})]
    res = subprocess.run(q, env=env, capture_output=True, text=True)
    try:
        verified = ok and json.loads(res.stdout).get('Color') == h_hex
    except Exception:
        verified = False
    t2 = time.perf_counter()
    return t1 - t0, t2 - t1, ok, verified, (p.stderr.strip().splitlines() or [''])[-1][-200:]


async def main():
    await mpc.start()
    m, pid = len(mpc.parties), mpc.pid
    sec = mpc.SecInt(args.bits) if args.bits else mpc.SecInt()
    p = sec.field.modulus
    rows = []
    run_id = f'{args.tag}_{int(time.time())}'
    for j in range(-args.warmup, args.trials):
        await mpc.output(mpc.input(sec(0), senders=0))          # synchronise parties before the trial
        b0 = sum(peer.protocol.nbytes_sent for peer in mpc.parties if peer.pid != pid)
        if args.preagg == 'on':
            v = party_vector(j, pid, m, args.k)
            dummy = np.zeros(args.k, dtype=np.int64)
            t0 = time.perf_counter()
            x = [mpc.input(sec.array(v if i == pid else dummy), senders=i) for i in range(m)]
            await mpc.gather(x)
            t1 = time.perf_counter()
            r = x[0]
            for y in x[1:]:
                r = r + y
            await mpc.gather(r)
            t2 = time.perf_counter()
            out = await mpc.output(r)
            t3 = time.perf_counter()
            out = np.array([int(z) for z in out], dtype=np.int64)
            t_share, t_eval, t_recon = t1 - t0, t2 - t1, t3 - t2
        else:
            G = party_genotypes(j, pid, m, args.k)
            t_share = t_eval = t_recon = 0.0
            parts = []
            for c0 in range(0, args.k, args.chunk):
                c1 = min(args.k, c0 + args.chunk)
                own = G[:, c0:c1]
                ta = time.perf_counter()
                x = [mpc.input(sec.array(own if i == pid else np.zeros((party_samples(i, m), c1 - c0), dtype=np.int64)),
                               senders=i) for i in range(m)]
                await mpc.gather(x)
                tb = time.perf_counter()
                r = x[0].sum(axis=0)
                for y in x[1:]:
                    r = r + y.sum(axis=0)
                await mpc.gather(r)
                tc = time.perf_counter()
                o = await mpc.output(r)
                td = time.perf_counter()
                parts.append(np.array([int(z) for z in o], dtype=np.int64))
                t_share += tb - ta; t_eval += tc - tb; t_recon += td - tc
                del x, r
            out = np.concatenate(parts)
        nb = sum(peer.protocol.nbytes_sent for peer in mpc.parties if peer.pid != pid) - b0
        if pid == 0:
            meta = json.dumps({'query_id': f'{args.tag}-{j}', 'parties': list(range(m)), 'k': args.k,
                               'consent_ref': 'synthetic'}, sort_keys=True).encode()
            th0 = time.perf_counter(); h = hashlib.sha256(enc_vec(out) + meta).hexdigest(); t_hash = time.perf_counter() - th0
            t_fab = t_ver = 0.0; fab_ok = ver_ok = ''; fab_msg = ''
            if args.fabric:
                t_fab, t_ver, fab_ok, ver_ok, fab_msg = fabric_commit(h, f'{run_id}_{j}')
            # plaintext oracle / baseline on the same inputs (independent NumPy path)
            if args.preagg == 'on':
                vs = [party_vector(j, i, m, args.k) for i in range(m)]
                tp0 = time.perf_counter(); oracle = np.sum(vs, axis=0); t_plain = time.perf_counter() - tp0
            else:
                gs = [party_genotypes(j, i, m, args.k) for i in range(m)]
                tp0 = time.perf_counter(); oracle = sum(g.sum(axis=0) for g in gs); t_plain = time.perf_counter() - tp0
                del gs
            if j >= 0:
                t_pipe = t_share + t_eval + t_recon + t_hash + t_fab + t_ver
                rows.append({'tag': args.tag, 'n': m, 't': mpc.threshold, 'k': args.k, 'preagg': args.preagg,
                             'p_bits': p.bit_length(), 'ssl': int(bool(mpc.options.ssl)), 'trial': j,
                             't_sharing_ms': t_share * 1e3, 't_eval_ms': t_eval * 1e3, 't_recon_ms': t_recon * 1e3,
                             't_online_ms': (t_eval + t_recon) * 1e3, 't_hash_ms': t_hash * 1e3,
                             't_fabric_commit_ms': t_fab * 1e3, 't_readback_verify_ms': t_ver * 1e3,
                             't_pipeline_ms': t_pipe * 1e3, 't_plain_numpy_ms': t_plain * 1e3,
                             'fabric_ok': fab_ok, 'readback_verified': ver_ok, 'fabric_last_msg': fab_msg,
                             'oracle_match': int(np.array_equal(out, oracle)), 'bytes_sent_party0': nb,
                             'rss_party0_mb': resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024})
    nbytes = sum(peer.protocol.nbytes_sent for peer in mpc.parties if peer.pid != pid)
    await mpc.shutdown()
    os.makedirs(args.out_dir, exist_ok=True)
    peak = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024
    with open(os.path.join(args.out_dir, f'mem_{args.tag}_p{pid}.json'), 'w') as f:
        json.dump({'tag': args.tag, 'n': m, 'k': args.k, 'pid': pid, 'peak_rss_mb': peak, 'bytes_sent_total': nbytes,
                   'iterations': args.trials + args.warmup, 'p_bits': p.bit_length(), 'preagg': args.preagg}, f)
    if pid == 0:
        with open(os.path.join(args.out_dir, f'trials_{args.tag}.csv'), 'w', newline='') as f:
            w = csv.DictWriter(f, fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)
        pl = np.array([r['t_pipeline_ms'] for r in rows]); on = np.array([r['t_online_ms'] for r in rows])
        print(f"n={m} t={mpc.threshold} k={args.k} preagg={args.preagg} N={len(rows)} pipeline mean={pl.mean():.1f}ms "
              f"online mean={on.mean():.3f}ms match={sum(r['oracle_match'] for r in rows)}/{len(rows)} "
              f"fabric_ok={sum(1 for r in rows if r['fabric_ok'] is True)} verified={sum(1 for r in rows if r['readback_verified'] is True)} "
              f"peakRSS_p0={peak:.1f}MB", flush=True)

mpc.run(main())
