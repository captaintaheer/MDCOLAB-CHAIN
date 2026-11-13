# AWS run, 12 November 2026

Raw data, environment records and logs of the multi-node evaluation on Amazon EC2
(ap-southeast-1a), and the scripts that build every AWS table and figure from them.
Times in file contents are Asia/Kuala_Lumpur (UTC+8) unless a log line states otherwise.

## Rebuild the tables and Figure 3

```bash
cd results/aws_2026-11-12
python make_tables.py              # tables/*.csv and tables/tables.md (NumPy only)
python check_reported_values.py    # compares the reported values with the rebuilt tables
python make_fig3.py                # figures/fig3_fabric.png (needs matplotlib)
```

## Setup

| Item | Value |
|---|---|
| SMPC nodes | 16 x c6i.large (2 vCPU, 4 GiB, Intel Xeon Platinum 8375C), one MPyC party per node |
| Fabric node | 1 x c6i.2xlarge (8 vCPU, 16 GiB); Fabric test-network in Docker; MPyC party 0 of the pipeline runs |
| Placement | ap-southeast-1a (AZ id apse1-az2), one cluster placement group, private IPs |
| Measured RTT | ICMP, 20 pings per ordered pair: SMPC to SMPC mean 0.151 ms (pair averages 0.090 to 0.318 ms), SMPC to Fabric node mean 0.244 ms |
| OS | Ubuntu 24.04.5 LTS, kernel 7.0.0-1014-aws |
| Python | 3.12.3; mpyc 0.9, numpy 1.26.4, psutil 7.2.2 |
| Fabric | 2.5.4 (peer, orderer, tools), fabric-ca 1.5.17, fabric-samples 7f0f4a2 test-network: 1 etcdraft orderer, one peer per org, LevelDB, TLS on (clientAuthRequired false), `asset-transfer-basic` Go chaincode; docker-ce 28.5.2 |
| Code | repository commit 03f1599; `layer-2/smpc_bench.py` for online SMPC, `harness/pipeline_bench.py` for the pipeline, `harness/fabric_bench.py` and `harness/fabric_config.sh` for Fabric |
| SMPC profile | MPyC default field (SecInt l=32, 64-bit prime), MPyC TLS off, threshold t = (n-1)//2 unless `-T t` is given |
| Repetitions | seed 20261017; 100 timed trials after 10 warm-ups per SMPC and pipeline configuration; Fabric: 100 sequential transactions or a 60 s open-loop window per offered load |

Deployment scripts and the order of operations: [`deploy/aws/`](../../deploy/aws/).

## Layout

| Path | Contents | Used for |
|---|---|---|
| `smpc_online/nN_kK/` | `trials_default_nN_kK.csv` (party 0, one row per trial), `mem_default_nN_kK_pI.json` (each party), `partyI.log`, `stdout.log`, `stderr.log`, `run_meta.json`; n in {4, 8, 12, 16}, k in {10 000, 50 000} | Table I (AWS rows), communication volume |
| `pipeline/bs10_bt0.2s_endorseMAJORITY_orgs2/nN_kK/` | `trials_pipeline_*.csv` (party 0, one row per trial), `mem_*_pI.json`, logs, `run_meta.json`; orderer BatchTimeout 0.2 s | Table III, stage breakdown |
| `pipeline/bs10_bt2s_endorseMAJORITY_orgs2/nN_kK[_tT]/` | same, BatchTimeout 2 s; `_tT` = threshold given with `-T` | Table III (values in parentheses), Table V |
| `pipeline/_failed_attempts/` | two attempts that did not complete and are not used (see below) | none |
| `fabric/<config>/<run>/` | `tx_log.csv` (one row per transaction), `resources.csv` (docker stats and host CPU every 2 s), `summary.json`, logs, `run_meta.json` | Table II, Figure 3 |
| `fabric/_network_configs/<config>/` | `configtx.diff`, `effective_channel_config.json`, `chaincode_definition.json`, network and chaincode deployment logs; `<config>.setup.log` | Fabric configuration evidence |
| `env/` | per-node environment (`instance_type`, AZ, placement group, CPU, memory, OS, kernel, Python packages, Docker), `fabric_samples_commit.txt`, `rtt_ping_fullmesh.txt` | setup |
| `logs/` | node setup log, orchestration logs, Fabric phase logs, Docker image list | provenance |
| `tables/` | output of `make_tables.py` | all AWS tables |
| `figures/` | output of `make_fig3.py` | Figure 3 |

Fabric configuration names: `bs<MaxMessageCount>_bt<BatchTimeout>_endorse<MAJORITY|ANY>_orgs<2|3>`.
Fabric run names: `seq_eE` (100 sequential transactions) or `rateR_eE[_c64]` (open loop at R tx/s for
60 s), E = endorsing peers targeted per transaction, `_c64` = 64 client workers (otherwise 16).

### Columns of the per-trial files

`smpc_online/*/trials_*.csv`: `tag, n, k, bits_l, p_bits, ssl, trial, t_sharing_ms, t_eval_ms, t_recon_ms,
t_online_ms, t_hash_ms, t_verify_ms, t_total_smpc_ms, oracle_match, hash_ok`.
`t_online_ms = t_eval_ms + t_recon_ms` is measured from the point where all input shares are held
until `await mpc.output(r)` returns; `t_sharing_ms` (secret sharing of the inputs) is reported separately.

`pipeline/*/*/trials_*.csv`: `tag, n, t, k, preagg, p_bits, ssl, trial, t_sharing_ms, t_eval_ms, t_recon_ms,
t_online_ms, t_hash_ms, t_fabric_commit_ms, t_readback_verify_ms, t_pipeline_ms, t_plain_numpy_ms,
fabric_ok, readback_verified, fabric_last_msg, oracle_match, bytes_sent_party0, rss_party0_mb`.
`t_pipeline_ms` is the sum of sharing, eval, recon, hash, Fabric commit (`--waitForEvent`) and
read-back/verify; `t_plain_numpy_ms` is the NumPy plaintext baseline on the same inputs.

`mem_*.json`: `peak_rss_mb` (ru_maxrss of the party process), `bytes_sent_total` and `iterations`
(warm-ups included in both).

`fabric/*/*/tx_log.csv`: `tx, txid, scheduled_ts, submit_ts, commit_ts, finality_s, rc, status, error`.

## Operational notes

* Fabric node setup: Ubuntu's `docker.io` 29.1.3 was replaced by docker-ce 28.5.2 and `golang-go` was
  installed before any Fabric measurement, because the Fabric 2.5.4 chaincode build failed with Docker
  API minimum version 1.44 and chaincode vendoring needs `go`.
* `harness/fabric_config.sh` was changed twice during the run: `set +u` before sourcing `envVar.sh`,
  and `set +euo pipefail` in the Org3 install subshell (the fabric-samples `queryinstalled | grep`
  check returns 1 before the package is installed). The setup logs of the failed 3-org attempts are in
  `fabric/_network_configs/_failed_attempts_orgs3/`. No measurement was taken on a network whose setup
  failed.
* `fabric/_network_configs/bs10_bt2s_endorseMAJORITY_orgs2_first_network/` is the configuration
  snapshot of the first network with that configuration (used for the sequential and 16-worker
  runs); the 64-worker runs used a recreated network with the same settings.
* With 16 client workers that each wait for their commit event, at most 16 transactions are pending,
  so 30- and 50-transaction blocks do not fill and every block waits for the BatchTimeout
  (`fabric/bs30_bt2s_endorseMAJORITY_orgs2/rate50_e2`). The block-size and 3-org grids were therefore
  run with 64 workers.
* `pipeline/_failed_attempts/n4_k100000_interrupted_ssh_drop/`: the SSH session to party 0 dropped
  during the run. `pipeline/_failed_attempts/n8_k10000_port_conflict_with_stale_run/`: the next run
  found the MPyC port still held by the interrupted parties. Both configurations were rerun from
  scratch after the stale processes were stopped, and the remaining pipeline runs were driven from
  the Fabric node (`deploy/aws/orchestrate_node.sh`).
* Private IP addresses are replaced by node labels (for example `<smpc-node03>`, `<fabric-node>`);
  instance, security-group, VPC, placement-group and snapshot IDs and the custom AMI ID are replaced by
  placeholders; public IP addresses and the account ID are not included.
