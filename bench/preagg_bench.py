#!/usr/bin/env python3
"""Layer-1 pre-aggregation timing on synthetic genotypes.
Party i holds the samples with sample_id mod n == i (2,504 samples total) as an int8 dosage matrix
(samples x k SNPs, values 0/1/2) and reduces it to an allele-count vector v_i (column sums).
Only the reduction is timed (matrix generation and VCF parsing are not included)."""
import csv, os, time, numpy as np
rows = []
for n in [3, 4, 5, 6, 7, 8, 12, 16]:
    for k in [10000, 50000, 100000]:
        ni = len(range(0, 2504, n))  # party 0 has the most samples
        G = np.random.default_rng([7, n, k]).integers(0, 3, size=(ni, k), dtype=np.int8)
        ts = []
        for rep in range(30):
            t = time.perf_counter(); v = G.sum(axis=0, dtype=np.int64); ts.append((time.perf_counter() - t) * 1e3)
        ts = np.array(ts[5:])
        rows.append({'n': n, 'k': k, 'samples_party0': ni, 'preagg_mean_ms': ts.mean(), 'preagg_sd_ms': ts.std(ddof=1),
                     'preagg_median_ms': np.median(ts), 'preagg_p95_ms': np.percentile(ts, 95), 'reps': len(ts)})
        print(rows[-1], flush=True)
root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
with open(os.path.join(root, 'results', 'preagg_synthetic.csv'), 'w', newline='') as f:
    w = csv.DictWriter(f, fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)
