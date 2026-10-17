#!/usr/bin/env python3
"""Layer-2 vector benchmark harness.

Each of the n parties holds a private allele-count vector v_i of dimension k and secret-shares it
with MPyC's Shamir sharing (mpc.input); the parties evaluate the linear circuit r = sum_i v_i and
reconstruct r (mpc.output). The result is checked against an independent NumPy plaintext oracle.

Run (all parties as local processes on one host):
    python smpc_bench.py -M 3 --k 10000 --trials 100 --warmup 10 [--bits 224] [--ssl]

Per trial, party 0 records with time.perf_counter():
    t_sharing   : mpc.input of all n vectors until every share is locally available (share generation +
                  distribution)
    t_eval      : local evaluation of the linear circuit (sum of shared vectors) until result shares exist
    t_recon     : `await mpc.output(r)` (reconstruction, includes one communication round)
    t_online    : t_eval + t_recon, from 'all parties hold shares' until r is available; the timer stops
                  after `await mpc.output(...)` returns
    t_hash      : SHA-256(enc(r) || enc(meta)) commitment
    t_verify    : consumer-side recomputation of the hash and comparison
The Fabric commit is not timed by this script.
Inputs are synthetic allele counts (Binomial(2*n_i, af)) for 2,504 samples split by sample-id mod n.
"""
import argparse, csv, hashlib, json, os, resource, struct, sys, time
import numpy as np
from mpyc.runtime import mpc

N_SAMPLES = 2504  # number of samples used to size the synthetic counts

ap = argparse.ArgumentParser()
ap.add_argument('--k', type=int, default=10000)
ap.add_argument('--trials', type=int, default=100)
ap.add_argument('--warmup', type=int, default=10)
ap.add_argument('--bits', type=int, default=None, help='SecInt bit length l (default: MPyC default, 32)')
ap.add_argument('--seed', type=int, default=20261017)
ap.add_argument('--out-dir', default='../results/raw/aligned')
ap.add_argument('--tag', default='run')
args, _ = ap.parse_known_args()   # MPyC parses its own options (-M, -I, --ssl, ...)

if mpc.options.ssl:   # MPyC reads the TLS files from .config/ in the working directory
    _need = ['mpyc_ca.crt'] + [f'party_{i}.{e}' for i in range(len(mpc.parties)) for e in ('crt', 'key')]
    _missing = [f for f in _need if not os.path.exists(os.path.join('.config', f))]
    if _missing:
        sys.exit(f"--ssl: {len(_missing)} TLS file(s) missing in {os.path.abspath('.config')} "
                 f"(e.g. {', '.join(_missing[:3])}). Run ./gen_certs.sh {len(mpc.parties)} in layer-2 first.")


def party_samples(pid, m):
    return sum(1 for s in range(N_SAMPLES) if s % m == pid)


def party_vector(trial, pid, m, k):
    af = np.random.default_rng([args.seed, trial + 1000, 10**6]).uniform(0.01, 0.5, k)
    rng = np.random.default_rng([args.seed, trial + 1000, pid])
    return rng.binomial(2 * party_samples(pid, m), af).astype(np.int64)


def enc_vec(r):
    r = np.asarray(r, dtype='<u8')
    return struct.pack('<Q', r.size) + r.tobytes()


async def main():
    await mpc.start()
    m, pid = len(mpc.parties), mpc.pid
    sec = mpc.SecInt(args.bits) if args.bits else mpc.SecInt()
    p = sec.field.modulus
    rss0 = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024
    rows = []
    for j in range(-args.warmup, args.trials):
        v = party_vector(j, pid, m, args.k)
        dummy = np.zeros(args.k, dtype=np.int64)
        await mpc.output(mpc.input(sec(0), senders=0))          # synchronise parties before the trial
        t0 = time.perf_counter()
        # NB: mpc.input(secure_array) with all senders at once hangs in MPyC 0.9, so input per sender.
        x = [mpc.input(sec.array(v if i == pid else dummy), senders=i) for i in range(m)]
        await mpc.gather(x)                                        # all shares held locally
        t1 = time.perf_counter()
        r = x[0]
        for y in x[1:]:
            r = r + y
        await mpc.gather(r)                                        # result shares computed
        t2 = time.perf_counter()
        out = await mpc.output(r)                                  # reconstruction
        t3 = time.perf_counter()
        out = np.array([int(z) for z in out], dtype=np.int64)
        meta = json.dumps({'query_id': f'{args.tag}-{j}', 'parties': list(range(m)), 'k': args.k,
                           'consent_ref': 'synthetic'}, sort_keys=True).encode()
        h = hashlib.sha256(enc_vec(out) + meta).hexdigest()
        t4 = time.perf_counter()
        ok_hash = hashlib.sha256(enc_vec(out) + meta).hexdigest() == h
        t5 = time.perf_counter()
        if pid == 0 and j >= 0:
            oracle = np.zeros(args.k, dtype=np.int64)
            for i in range(m):
                oracle += party_vector(j, i, m, args.k)      # independent plaintext path (NumPy)
            rows.append({'tag': args.tag, 'n': m, 'k': args.k, 'bits_l': sec.bit_length,
                         'p_bits': p.bit_length(), 'ssl': int(bool(mpc.options.ssl)), 'trial': j,
                         't_sharing_ms': (t1 - t0) * 1e3, 't_eval_ms': (t2 - t1) * 1e3,
                         't_recon_ms': (t3 - t2) * 1e3, 't_online_ms': (t3 - t1) * 1e3,
                         't_hash_ms': (t4 - t3) * 1e3, 't_verify_ms': (t5 - t4) * 1e3,
                         't_total_smpc_ms': (t5 - t0) * 1e3,
                         'oracle_match': int(np.array_equal(out, oracle)), 'hash_ok': int(ok_hash)})
    nbytes = sum(peer.protocol.nbytes_sent for peer in mpc.parties if peer.pid != pid)
    await mpc.shutdown()
    os.makedirs(args.out_dir, exist_ok=True)
    peak = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024   # Linux: KiB -> MiB
    with open(os.path.join(args.out_dir, f'mem_{args.tag}_p{pid}.json'), 'w') as f:
        json.dump({'tag': args.tag, 'n': m, 'k': args.k, 'pid': pid, 'peak_rss_mb': peak,
                   'rss_after_start_mb': rss0, 'bytes_sent_total': nbytes,
                   'iterations': args.trials + args.warmup, 'p': str(p), 'p_bits': p.bit_length(),
                   'ssl': bool(mpc.options.ssl)}, f)
    if pid == 0:
        with open(os.path.join(args.out_dir, f'trials_{args.tag}.csv'), 'w', newline='') as f:
            w = csv.DictWriter(f, fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)
        on = np.array([r['t_online_ms'] for r in rows])
        print(f"n={m} k={args.k} p_bits={p.bit_length()} ssl={mpc.options.ssl} online mean={on.mean():.3f}ms "
              f"median={np.median(on):.3f} p95={np.percentile(on,95):.3f} match={sum(r['oracle_match'] for r in rows)}/{len(rows)} "
              f"peakRSS={peak:.1f}MB", flush=True)

mpc.run(main())
