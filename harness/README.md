# Benchmark harness

Scripts used for the AWS run of 12 Nov 2026 (`results/aws_2026-11-12/`). They use the repository
code unchanged; `layer-2/smpc_bench.py` is used directly for the online SMPC measurements.

| File | Purpose | Used for |
|---|---|---|
| `pipeline_bench.py` | Full pipeline per trial: secret sharing, online aggregation (`t_online = t_eval + t_recon`), SHA-256 commitment, Fabric commit with `--waitForEvent`, ReadAsset read-back and digest comparison, NumPy plaintext oracle. One CSV row per trial (party 0) and one memory JSON per party. | Table III, Table V, per-stage breakdown |
| `fabric_bench.py` | Fabric load generator using the peer CLI (`CreateAsset`, `--waitForEvent`): sequential mode (`--rate 0`) and open-loop offered load (`--rate R --concurrency C`). Writes `tx_log.csv`, `resources.csv`, `summary.json`. | Table II, Fig. 3 |
| `fabric_config.sh` | Recreates the Fabric test-network with a given BatchTimeout, MaxMessageCount, org count (2 or 3) and endorsement policy (majority or any), deploys `asset-transfer-basic` (Go) and snapshots the effective channel configuration. | Table II, Table III |
| `configtx.stock.yaml` | Unmodified `test-network/configtx/configtx.yaml` from fabric-samples 7f0f4a2, the base that `fabric_config.sh` edits. | Table II, Table III |
| `runexp.py` | Runs one command, captures `stdout.log`/`stderr.log` and writes `run_meta.json` (command, parameters, host, start/end time, git commit, exit status). | all runs |

Environment variables:

* `FABRIC_TEST_NETWORK`: test-network directory (default for `fabric_config.sh`: `../layer-3/fabric-samples/test-network` relative to this folder; required by `fabric_bench.py` and by `pipeline_bench.py --fabric`).
* `HARNESS_DIR`: location of this folder for `fabric_config.sh` (default: the script's own directory).
* `MDC_REPO`: repository path whose `git rev-parse HEAD` is recorded by `runexp.py` (default: current directory).

Examples (single host, all parties as local processes):

```bash
# online SMPC, n = 3 parties, k = 1000, 5 trials after 1 warm-up
(cd layer-2 && python smpc_bench.py -M 3 --k 1000 --trials 5 --warmup 1 --seed 20261017 --tag demo --out-dir /tmp/demo_smpc)

# pipeline without the ledger step
python harness/pipeline_bench.py -M 3 --k 1000 --trials 5 --warmup 1 --seed 20261017 --tag demo --out-dir /tmp/demo_pipe

# pipeline with Fabric (requires a running test-network with the basic chaincode)
export FABRIC_TEST_NETWORK=$PWD/layer-3/fabric-samples/test-network
python harness/pipeline_bench.py -M 4 --k 10000 --trials 100 --warmup 10 --seed 20261017 --fabric --tag n4_k10000 --out-dir /tmp/pipe_n4

# Fabric configuration and load
harness/fabric_config.sh 2s 10 2 majority /tmp/cfg_bs10
python harness/fabric_bench.py --rate 0 --txs 100 --endorsers 2 --out-dir /tmp/fab_seq --tag seq
python harness/fabric_bench.py --rate 100 --duration 60 --concurrency 64 --endorsers 2 --out-dir /tmp/fab_r100 --tag r100
```

The multi-host commands used on AWS are in [`../deploy/aws/`](../deploy/aws/).
