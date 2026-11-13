# Ledger read-back integrity check

## What is checked

After a result hash has been committed, the consumer side reads the asset back from the ledger
and compares the stored value with the locally computed SHA-256 digest.

| Code path | Where | Check |
|---|---|---|
| End-to-end automation | `automate_layers.py`, `collect_ledger_metrics()` | `ReadAsset` of the last committed asset; the `Color`/`hash`/`value` field must equal `layer-2/output/result_hash.txt`. Reported as `Integrity OK` and `Integrity Check` in the metrics report. |
| Pipeline benchmark | `harness/pipeline_bench.py`, `fabric_commit()` | Every trial: `CreateAsset` with `--waitForEvent`, then `ReadAsset`; `readback_verified` is True when the stored `Color` equals the digest of that trial. |

## Why the first report showed Integrity OK False

The first report ([`results/legacy/metrics_report_2026-09-21.md`](../results/legacy/metrics_report_2026-09-21.md))
shows `Integrity OK False` together with `Query Latency 0.0` and `Tx Success Rate 1.0`. In the code
of that version, `Query Latency` stays 0.0 only when the `ReadAsset` command exits with an error;
a readable asset with a different value would have produced a non-zero query latency. Its TPS
value shows that the ledger step ran in throughput mode (see [RECONCILIATION.md](RECONCILIATION.md)),
where invokes are sent without `--waitForEvent`: the peer CLI returns once the orderer has accepted
the transaction, and the block is cut only after the BatchTimeout (2 s in the stock test-network).
The final `ReadAsset` was issued immediately after the last invoke returned, so it could run before
the asset was committed and fail with "asset ... does not exist". The error text of that run was
not kept; this is the cause consistent with all values in the report.

## Change

Commit "fix(ledger): wait for commit before the read-back integrity check" changes
`collect_ledger_metrics()` to:

* repeat `ReadAsset` every 0.5 s while the peer answers "does not exist", up to
  `READBACK_TIMEOUT_S` seconds (default 15);
* record the outcome in `integrity_reason`: `digest_match`, `digest_mismatch`,
  `unparseable_asset`, `query_failed: <error>` or `no_successful_invoke`;
* print `[integrity] asset=... attempts=... result=...` and add an `Integrity Check` row to the report.

## Tests

`tests/test_integrity_readback.py` replaces the Fabric peer CLI with a stub that accepts every
invoke and makes an asset readable only after a set number of queries (an accepted but not yet
committed transaction). It runs without Docker or Fabric.

| Test | Stub behaviour | Expected result |
|---|---|---|
| `test_pending_commit_single_query_fails` | asset visible after 3 queries; `READBACK_TIMEOUT_S=0` (one query, as before the change) | `integrity_ok` False, `query_failed`, query latency 0.0 |
| `test_pending_commit_polling_matches` | asset visible after 3 queries; default timeout | `integrity_ok` True, `digest_match` |
| `test_tampered_value_is_detected` | stored value differs from the digest | `integrity_ok` False, `digest_mismatch` |

The same stub run against `collect_ledger_metrics()` of commit 03f1599 (before the change) returns
`integrity_ok False`, `query_latency 0.0`, `tx_success_rate 1.0`, the pattern of the first report.
Commands and output: [REPRODUCTION_TEST.md](REPRODUCTION_TEST.md).

## Evidence from the AWS run

The AWS pipeline runs use `harness/pipeline_bench.py`, which waits for the commit event before
reading back. Over the 23 pipeline configurations (2,300 timed trials), `fabric_ok` and
`readback_verified` are True in 2,300 of 2,300 trials
(`results/aws_2026-11-12/tables/correctness_totals.csv`, from the `readback_verified` column of the
per-trial CSVs).

`automate_layers.py` itself was not rerun against a live Fabric network after the change, because
no Docker host was available for that test; the change is covered by the stub tests above.
