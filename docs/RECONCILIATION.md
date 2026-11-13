# Reconciliation of the first metrics report with the reported results

The first version of the repository (commit 8695ca4, 21 Sep 2026) contained a report written by
`automate_layers.py`, now kept as
[`results/legacy/metrics_report_2026-09-21.md`](../results/legacy/metrics_report_2026-09-21.md).
Its values come from one end-to-end run of the original automation script and measure different
quantities from the evaluation reported for the AWS run
([`results/aws_2026-11-12/`](../results/aws_2026-11-12/)). The table explains each value from the
code at commit 8695ca4 (`automate_layers.py` and `layer-2/layer2_smpc.py`). The command line and the
console output of that run were not kept, so run settings that are not visible in the report are
derived from the values and stated as such.

| Metric in the first report | Value | What the code measured | Reported metric it relates to | Status |
|---|---|---|---|---|
| SMPC Exec Time / Latency | 0.0056 s | Wall time of `layer2_smpc.py` from before `mpc.start()` to after `mpc.shutdown()` (l.16 to l.42), around `--num_ops` sums of the three integers in `layer-1/shares.json`. `automate_layers.py` l.154 started `python -m mpyc layer2_smpc.py ...`; with MPyC 0.9 this starts the MPyC asyncio console and does not run the script (checked with `python -m mpyc layer2_smpc.py --num_ops 5 -M 1 < /dev/null`, which prints the console banner and the preloaded imports only), so no metrics were parsed and the fallback at l.173 ran `layer2_smpc.py` without `-M`, i.e. with a single party. In addition, l.801 uses one party unless `--allow_multi_smpc` is given. | Online SMPC time (Table I): `t_eval + t_recon` of `layer-2/smpc_bench.py` for k-dimensional vectors with n parties on separate nodes. | Not comparable: single party, three scalars, includes runtime start and shutdown. |
| SMPC Throughput | 891.3 ops/s | `num_ops / execution_time`; 5 / 0.0056 s, consistent with the default `--smpc_ops 5`. | none | Not used. |
| SMPC Comm Rounds | 5 | `comm_rounds = args.num_ops` (l.38), a count of loop iterations, not measured rounds. | none | Not a measurement. |
| SMPC Comm Bytes | 0 | Bytes sent to other parties (l.36 to l.37); 0 because only one party ran. | Bytes sent per party per trial, 0.40 to 11.0 MB (`mem_*.json`). | Confirms the single-party run. |
| SMPC Peak RAM | 41.42 MB | RSS of the single `layer2_smpc.py` process. | Peak RSS per party (Table I, Table III). | Not comparable (different workload). |
| Plaintext Exec Time | 0.0004 s | `collect_plaintext_baseline`: reading `layer-2/output/result.txt` and a 5-iteration loop that assigns the value. | NumPy plaintext baseline `t_plain_numpy_ms` (0.30 ms at n = 8, k = 10 000). | Not comparable. |
| Overhead Exec Time | 13.6961x | Ratio of the two values above. | none | Not used. |
| TPS | 26.9546 | `successes / total batch time` in `collect_ledger_metrics`. In the sequential paths (l.284, correctness mode or concurrency 1) every invoke completes before the next starts, so TPS cannot exceed 1 / mean latency = 1 / 0.5831 s = 1.71. A value of 26.95 is only possible in the concurrent path (l.333: `--mode throughput` with `--ledger_concurrency` above 1), where invokes are sent without `--waitForEvent`. TPS x latency = 15.7 invokes in flight on average. | Committed TPS (Table II): VALID commits per second with `--waitForEvent` for every transaction (`harness/fabric_bench.py`). | Not comparable: counts accepted submissions, not commits. |
| Tx Latency Avg | 0.5831 s | Mean wall time of the peer CLI invoke. Without `--waitForEvent` the CLI returns once the orderer has accepted the transaction, before it is committed. | Mean finality, submit to commit event (Table II). | Not comparable. |
| Query Latency | 0.0 | Time of the final `ReadAsset`; the code reports 0.0 when the query exits with an error (`qlat` stays `None`). | Read-back/verify, 44.3 ms (stage breakdown). | Shows the final query failed. |
| Tx Success Rate | 1.0 | Invokes that returned exit status 0 / invokes sent. | Fabric runs: VALID / submitted. | Submission success only. |
| Peer Peak CPU / RAM | 3.56 % / 114.7 MB | Peaks of `docker stats` samples for the peer and orderer containers. | `fabric/*/*/resources.csv` | Not used in the tables. |
| End-to-End Latency | 65.78 s | Wall time of the whole `automate_layers.py` run from l.789: Layer 1 FASTA processing, Layer 2 share files, the SMPC step (the MPyC console reads from the terminal until the timeout, default 10 s, when the script is started from a terminal; the console start is not timed separately), the single-party fallback, the Layer 3 step, and the ledger batch. | Pipeline latency per job (Table III): sharing to verified read-back for one aggregation. | Not comparable: includes set-up and a timeout. |
| Integrity OK | False | Final `ReadAsset` of the last asset; False when the query fails or the stored value differs from `result_hash.txt`. | Read-back verification, 2,300 of 2,300 pipeline trials verified. | Explained and fixed: see [INTEGRITY_CHECK.md](INTEGRITY_CHECK.md). |

## Where each reported number comes from

All AWS values are rebuilt from raw files by `results/aws_2026-11-12/make_tables.py`, and
`results/aws_2026-11-12/check_reported_values.py` compares them with the reported values. The
mapping from each table and figure to its script and files is in [MANIFEST.md](MANIFEST.md).

`check.txt` at the repository root lists target values used by `automate_layers.py --save_check_charts`
to draw comparison charts. It is an input of that option, not a record of measured results.
