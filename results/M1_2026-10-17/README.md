# Legacy results (not used for the reported tables)

This folder keeps earlier outputs unchanged for traceability. None of the tables or figures
reported for the AWS evaluation are computed from these files; those come from
[`../aws_2026-11-12/`](../aws_2026-11-12/) (see [`docs/MANIFEST.md`](../../docs/MANIFEST.md)).

| Path | What it is | Produced by |
|---|---|---|
| `metrics_report_2026-09-21.md` | Report written by `automate_layers.py` in the first version of the repository (commit 8695ca4, 21 Sep 2026). It was previously at the repository root as `metrics_report.md`. Its values (for example SMPC 0.0056 s, TPS 26.9546, end-to-end 65.78 s, Integrity OK False) are explained in [`docs/RECONCILIATION.md`](../../docs/RECONCILIATION.md). | `automate_layers.py` |
| `M1_2026-10-17/` | Single-host M1 benchmark run of 17 Oct 2026 (commit 47bd6ae): online SMPC grid for two profiles, runs of the original `layer-2/layer2_smpc.py`, and the pre-aggregation comparison. All parties ran as local processes on one machine. | `bench/run_grid.py`, `bench/summarize.py`, `bench/run_original_smpc.py`, `bench/preagg_bench.py` |

Profiles in `M1_2026-10-17/`:

* `aligned`: `--ssl --bits 224` (MPyC TLS on, about 256-bit prime field), n in {3..8, 12, 16}, k in {10 000, 50 000, 100 000}, 100 trials after 10 warm-ups.
* `default`: MPyC default field (64-bit prime), TLS off, k = 10 000 only.

To print the tables for this run:

```bash
MDCOLAB_RESULTS=results/legacy/M1_2026-10-17 python bench/make_tables.py
```

The `original_pipeline_report_*.md` files in `M1_2026-10-17/raw/` are `automate_layers.py`
reports and embed charts as base64 PNG data.
