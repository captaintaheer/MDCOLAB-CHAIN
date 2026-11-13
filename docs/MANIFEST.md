# Manifest: tables and figures

Paths are relative to the repository root. `AWS` = `results/aws_2026-11-12`. Every AWS value is
rebuilt with:

```bash
cd results/aws_2026-11-12
python make_tables.py && python check_reported_values.py && python make_fig3.py
```

| Item | Content | Script | Output file | Raw data |
|---|---|---|---|---|
| Table I, multi-node rows | Online SMPC time and mean per-party peak RSS, n in {4, 8, 12, 16}, k in {10 000, 50 000}; SD and 95% CI in the footnote | `layer-2/smpc_bench.py` (measurement, `deploy/aws/run_smpc_aws.sh`), `AWS/make_tables.py` | `AWS/tables/table1_smpc_online_grid.csv` (`online_mean_ms`, `peak_rss_mean_mb`, `online_sd_ms`, `online_ci95_ms`) | `AWS/smpc_online/nN_kK/trials_default_nN_kK.csv`, `mem_default_nN_kK_pI.json` |
| Table I, edge rows | Apple M1 single-host values (0.5 ms / 41.67 MB at k = 10 000; 4.39 ms / 72.4 MB at k = 100 000) | `layer-2/smpc_bench.py` | none | Per-trial files of the M1 runs are not included in this repository |
| Table II | Lone-transaction finality (BatchTimeout 0.2 s / 2 s), finality and committed TPS at 50 tx/s, maximum committed TPS (majority, 2 and 3 orgs; 1-of-n); footnote SD, p95, p99 and transaction counts | `harness/fabric_config.sh`, `harness/fabric_bench.py` (`deploy/aws/aws_fabric.sh`), `AWS/make_tables.py` | `AWS/tables/table2_fabric_summary.csv`; every run: `AWS/tables/table2_fabric_all_runs.csv` | `AWS/fabric/<config>/<run>/tx_log.csv`, `summary.json`; configuration snapshots in `AWS/fabric/_network_configs/` |
| Table III | Pipeline latency (BatchTimeout 0.2 s, 2 s in parentheses), jobs/s, party-0 peak RSS; footnote SD, commit, read-back, sharing and online ranges | `harness/pipeline_bench.py` (`deploy/aws/run_pipeline_aws.sh`, `node_run_pipeline.sh`), `AWS/make_tables.py` | `AWS/tables/table3_pipeline_bt0p2s.csv`, `AWS/tables/table3_pipeline_bt2s.csv` | `AWS/pipeline/<config>/nN_kK/trials_pipeline_*.csv`, `mem_*_pI.json` |
| Stage breakdown (Section V-C) | n = 8, k = 10 000, BatchTimeout 0.2 s: sharing, online, hash, commit, read-back, total | as Table III | `AWS/tables/table3_pipeline_bt0p2s.csv`; all configurations in [PIPELINE_STAGES.md](PIPELINE_STAGES.md) | as Table III |
| Table IV, MDCOLAB-CHAIN row | 0.21 s (Table II, finality at 50 tx/s), 61.5 TPS (Table II, maximum majority), 41.67 MB (Table I edge row) | as Tables I and II | as Tables I and II | as Tables I and II; the other rows are values published in the cited papers |
| Table V | Pipeline latency, party-0 peak RSS and oracle match versus n (default threshold) and versus t (n = 8), BatchTimeout 2 s; baselines in the footnote | `harness/pipeline_bench.py` (`-T t` for the threshold rows), `AWS/make_tables.py` | `AWS/tables/table5_components.csv`; baselines from `AWS/tables/table3_pipeline_bt0p2s.csv` (`plain_numpy_mean_ms`, `sharing_mean_ms` + `online_mean_ms`) | `AWS/pipeline/bs10_bt2s_endorseMAJORITY_orgs2/nN_k10000[_tT]/` |
| Table VI | Mapping of design features to GA4GH, GDPR, HIPAA and CARE/OCAP considerations | none (design mapping) | none | none |
| Figure 1 | Architecture diagram | none | none | none |
| Figure 2 | Edge (Apple M1) online time and peak memory versus k | none | none | Per-trial files of the M1 runs are not included in this repository |
| Figure 3 | Fabric committed TPS and mean finality, one factor at a time (offered 100 tx/s, 64 clients, BatchTimeout 2 s) | `AWS/make_fig3.py` | `AWS/figures/fig3_fabric.png`, values in `AWS/tables/fig3_values.csv` | as Table II |
| Correctness (Section V-F) | 3,100 trials with oracle match (800 SMPC, 2,300 pipeline); 2,300 of 2,300 read-backs verified | `AWS/make_tables.py` | `AWS/tables/correctness_totals.csv` | `oracle_match`, `readback_verified` columns of the per-trial CSVs |
| Communication volume | 0.40 to 11.0 MB sent per party per trial (1.00 MB at n = 8, k = 10 000) | `AWS/make_tables.py` | `AWS/tables/table1_smpc_online_grid.csv` (`sent_per_party_per_trial_mean_mb`) | `bytes_sent_total` and `iterations` in `AWS/smpc_online/*/mem_*.json` |
| Inter-node RTT (Section IV-B) | SMPC to SMPC mean 0.151 ms, SMPC to Fabric node 0.244 ms | `deploy/aws/pssh.sh` (measurement), `AWS/make_tables.py` | `AWS/tables/rtt_summary.csv` | `AWS/env/rtt_ping_fullmesh.txt` |

Earlier outputs that are not used for these tables are described in
[`results/legacy/README.md`](../results/legacy/README.md).
