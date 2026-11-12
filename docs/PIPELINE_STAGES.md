# Pipeline latency by stage, every (n, k) configuration

AWS run of 12 Nov 2026, 2 orgs, block size 10, majority endorsement; 100 trials after 10 warm-ups per row.
Party 0 runs on the Fabric node (c6i.2xlarge), parties 1..n-1 one per c6i.large node.
Values are means over trials unless stated, taken from the CSV files named in each heading
(built by `results/aws_2026-11-12/make_tables.py` from the per-trial files in
`results/aws_2026-11-12/pipeline/`).

Stages, as timed by `harness/pipeline_bench.py` on party 0:

| Stage | Timer |
|---|---|
| sharing | `mpc.input` of all n vectors until every share is held |
| eval | local sum of the shared vectors until result shares exist |
| recon | `await mpc.output(r)` |
| online | eval + recon |
| hash | SHA-256 of the encoded result and metadata |
| Fabric commit | peer CLI `CreateAsset` with `--waitForEvent`, until the Org1 peer reports the commit |
| read-back/verify | peer CLI `ReadAsset` and comparison of the stored digest with the computed one |
| total | sum of all stages (`t_pipeline_ms`) |

### BatchTimeout 0.2 s (`tables/table3_pipeline_bt0p2s.csv`)

| n | t | k | sharing (ms) | eval (ms) | recon (ms) | online (ms) | hash (ms) | Fabric commit (ms) | read-back/verify (ms) | total (s) | SD (s) | jobs/s | party-0 peak RSS (MB) | max peak RSS, other parties (MB) | sent per party per trial (MB) | oracle match | read-back verified |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 4 | 1 | 10000 | 29.9 | 3.01 | 4.85 | 7.86 | 0.108 | 279.7 | 44.3 | 0.362 | 0.002 | 2.76 | 48.9 | 47.5 | 0.40 | 100/100 | 100/100 |
| 4 | 1 | 50000 | 154.6 | 16.76 | 26.98 | 43.74 | 0.475 | 280.2 | 44.5 | 0.523 | 0.005 | 1.91 | 76.2 | 72.2 | 2.00 | 100/100 | 100/100 |
| 4 | 1 | 100000 | 309.4 | 34.28 | 55.23 | 89.51 | 0.989 | 279.8 | 44.2 | 0.724 | 0.013 | 1.38 | 110.7 | 105.2 | 4.00 | 100/100 | 100/100 |
| 8 | 3 | 10000 | 86.4 | 6.37 | 7.55 | 13.92 | 0.109 | 279.7 | 44.3 | 0.424 | 0.003 | 2.36 | 56.6 | 55.0 | 1.00 | 100/100 | 100/100 |
| 8 | 3 | 50000 | 437.1 | 37.29 | 40.78 | 78.07 | 0.471 | 280.3 | 44.6 | 0.840 | 0.007 | 1.19 | 113.0 | 108.6 | 5.00 | 100/100 | 100/100 |
| 8 | 3 | 100000 | 871.0 | 77.66 | 83.84 | 161.50 | 0.978 | 279.5 | 44.3 | 1.357 | 0.013 | 0.74 | 187.8 | 177.8 | 10.00 | 100/100 | 100/100 |
| 12 | 5 | 10000 | 151.1 | 9.41 | 10.39 | 19.80 | 0.111 | 279.7 | 44.2 | 0.495 | 0.003 | 2.02 | 63.5 | 61.7 | 1.60 | 100/100 | 100/100 |
| 12 | 5 | 50000 | 753.0 | 55.02 | 54.77 | 109.79 | 0.474 | 279.4 | 44.3 | 1.187 | 0.010 | 0.84 | 147.4 | 140.3 | 8.00 | 100/100 | 100/100 |
| 16 | 7 | 10000 | 223.9 | 12.49 | 15.61 | 28.10 | 0.110 | 279.6 | 44.4 | 0.576 | 0.005 | 1.74 | 71.9 | 69.7 | 2.20 | 100/100 | 100/100 |
| 16 | 7 | 50000 | 1104.5 | 71.39 | 75.85 | 147.24 | 0.473 | 279.9 | 44.3 | 1.576 | 0.006 | 0.63 | 182.2 | 174.0 | 11.00 | 100/100 | 100/100 |

### BatchTimeout 2 s (`tables/table3_pipeline_bt2s.csv`)

| n | t | k | sharing (ms) | eval (ms) | recon (ms) | online (ms) | hash (ms) | Fabric commit (ms) | read-back/verify (ms) | total (s) | SD (s) | jobs/s | party-0 peak RSS (MB) | max peak RSS, other parties (MB) | sent per party per trial (MB) | oracle match | read-back verified |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 4 | 1 | 10000 | 30.3 | 3.05 | 4.92 | 7.97 | 0.108 | 2080.8 | 44.7 | 2.164 | 0.004 | 0.46 | 48.6 | 47.4 | 0.40 | 100/100 | 100/100 |
| 4 | 1 | 50000 | 155.2 | 17.48 | 27.92 | 45.40 | 0.478 | 2080.8 | 44.8 | 2.327 | 0.003 | 0.43 | 76.2 | 72.8 | 2.00 | 100/100 | 100/100 |
| 4 | 1 | 100000 | 311.0 | 35.25 | 55.90 | 91.14 | 0.994 | 2081.0 | 44.9 | 2.529 | 0.009 | 0.40 | 110.7 | 104.7 | 4.00 | 100/100 | 100/100 |
| 8 | 3 | 10000 | 87.0 | 6.42 | 7.68 | 14.10 | 0.110 | 2080.8 | 44.8 | 2.227 | 0.003 | 0.45 | 56.6 | 55.1 | 1.00 | 100/100 | 100/100 |
| 8 | 1 | 10000 | 43.9 | 6.53 | 4.91 | 11.44 | 0.108 | 2080.2 | 44.5 | 2.180 | 0.003 | 0.46 | 54.0 | 52.5 | 0.80 | 100/100 | 100/100 |
| 8 | 2 | 10000 | 65.8 | 6.43 | 6.15 | 12.58 | 0.109 | 2080.3 | 44.5 | 2.203 | 0.002 | 0.45 | 55.6 | 54.0 | 0.90 | 100/100 | 100/100 |
| 8 | 3 | 10000 | 87.1 | 6.40 | 7.72 | 14.12 | 0.111 | 2080.0 | 44.4 | 2.226 | 0.003 | 0.45 | 56.5 | 55.1 | 1.00 | 100/100 | 100/100 |
| 8 | 3 | 50000 | 438.4 | 37.01 | 41.31 | 78.33 | 0.474 | 2080.4 | 44.8 | 2.642 | 0.006 | 0.38 | 113.6 | 108.9 | 5.00 | 100/100 | 100/100 |
| 8 | 3 | 100000 | 870.4 | 79.03 | 84.09 | 163.12 | 0.983 | 2080.2 | 44.6 | 3.159 | 0.014 | 0.32 | 185.8 | 176.9 | 10.00 | 100/100 | 100/100 |
| 12 | 5 | 10000 | 151.2 | 9.49 | 10.75 | 20.25 | 0.110 | 2080.0 | 44.6 | 2.296 | 0.003 | 0.44 | 63.2 | 61.7 | 1.60 | 100/100 | 100/100 |
| 12 | 5 | 50000 | 756.0 | 55.90 | 55.22 | 111.12 | 0.472 | 2080.3 | 44.7 | 2.993 | 0.012 | 0.33 | 148.5 | 141.1 | 8.00 | 100/100 | 100/100 |
| 16 | 7 | 10000 | 224.6 | 12.78 | 16.33 | 29.10 | 0.114 | 2080.2 | 44.5 | 2.378 | 0.004 | 0.42 | 72.1 | 69.8 | 2.20 | 100/100 | 100/100 |
| 16 | 7 | 50000 | 1117.4 | 72.62 | 78.63 | 151.25 | 0.473 | 2080.0 | 44.5 | 3.394 | 0.012 | 0.29 | 181.4 | 174.0 | 11.00 | 100/100 | 100/100 |

Observations from these tables:

* The Fabric commit is close to the orderer BatchTimeout plus about 80 ms (279.4 to 280.3 ms at 0.2 s,
  2079.97 to 2080.98 ms at 2 s): with one transaction per job, every block is cut by the timeout.
* Read-back/verify is 44.2 to 44.9 ms in every configuration.
* The growth of the total with n and k comes from secret sharing and the online phase; at
  n = 16, k = 50 000 sharing is 1104.5 ms (BatchTimeout 0.2 s).
* The `n8_k10000_t1`, `_t2` and `_t3` rows (BatchTimeout 2 s) are the threshold runs of Table V;
  the row without `_t` uses the default threshold t = 3.
