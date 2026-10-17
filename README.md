# MDCOLAB-CHAIN

Code accompanying the manuscript *"Empirical Validation, Regulatory Alignment and Design Lessons of a
Lightweight SMPC–Blockchain Framework for Genomic Privacy"* (JAIT-23816).

## 1. Overview

The framework is organised in four layers.

| Layer | Files |
|---|---|
| 1. Pre-aggregation and secret sharing | `layer-1/generate_shares.py` computes the G+C count of a FASTA file, splits it into three shares written to `layer-2/Input-P{0,1,2}-0`, and writes metadata to `layer-1/shares.json`. `layer-1/layer1_data_input.py` is a standalone secret-sharing example using the `secretsharing` package. |
| 2. SMPC aggregation (MPyC) | `layer-2/compute_sum.py` reads the three share files, computes their sum and writes `result.txt` with its SHA-256 hash. `layer-2/layer2_smpc.py` performs an MPyC secure sum and prints execution time, memory and communication figures. `layer-2/metrics_collector.py` contains helpers that run and parse these metrics. `layer-2/smpc_bench.py` is a vector benchmark in which each party secret-shares a k-dimensional allele-count vector, the parties compute the sum and reconstruct it, and the result is checked against a NumPy oracle. `layer-2/gen_certs.sh` creates TLS certificates for MPyC's `--ssl` option. |
| 3. Hyperledger Fabric ledger | `automate_layers.py` runs `layer-3/fabric-samples/test-network/blockchain.py` and uses the `peer` CLI to record result hashes with the `basic` chaincode (`CreateAsset`) on channel `mychannel`, then reads them back (`ReadAsset`) to measure latency and throughput. See `layer-3/README.md` and §5. |
| 4. Consent and dissemination | Part of the framework design; this repository contains no code for this layer. |

Other files:

* `automate_layers.py`: orchestrator that runs Layers 1–3 in sequence, collects metrics and writes a
  Markdown report with charts.
* `bench/`: benchmark scripts. `run_grid.py` (runs `smpc_bench.py` over a grid of n and k),
  `summarize.py` (summary statistics), `make_tables.py` (Markdown tables from the CSVs),
  `preagg_bench.py` (pre-aggregation timing on synthetic genotypes) and `run_original_smpc.py`
  (repeated runs of `layer2_smpc.py`).
* `check.txt`: chart specification notes used by `automate_layers.py --save_check_charts`.
* `metrics_report.md`: a report produced by `automate_layers.py`.
* `tps.py`: helper snippet that reads values from `metrics_report.md`.
* `requirements.txt`: Python dependencies.

## 2. Requirements and setup

* Python 3.12 (MPyC 0.9 requires `numpy<2`, which has no wheels for Python 3.13).
* For Layer 3: Docker and the Hyperledger Fabric binaries (see §5).
* `openssl`, if TLS between MPyC parties is used.

```bash
python3.12 -m venv venv               # or: uv venv -p 3.12 venv
. venv/bin/activate
pip install -r requirements.txt       # mpyc==0.9, numpy<2, psutil, matplotlib
```

`gmpy2` is optional; MPyC uses it for faster arithmetic when installed.

## 3. Running the pipeline

```bash
python automate_layers.py --genome data/<file>.fna --allow_multi_smpc --smpc_parties 3 \
       --report_path results/raw/my_report.md
```

Main options of `automate_layers.py`:

| Flag | Default | Meaning |
|---|---|---|
| `--genome PATH` | `data/genome.fna` | FASTA input for Layer 1 |
| `--report_path PATH` | `metrics_report.md` | where the Markdown report is written |
| `--allow_multi_smpc` | off | run `layer2_smpc.py` with `--smpc_parties` parties (otherwise one party) |
| `--smpc_parties N` | 3 | number of MPyC parties |
| `--smpc_ops N` | 5 | number of secure operations per SMPC run |
| `--smpc_python PATH` | auto | Python interpreter with MPyC installed |
| `--smpc_timeout_s S` | 10 | timeout for the SMPC metrics run |
| `--ledger_txs N` | 3 | number of ledger transactions |
| `--ledger_concurrency N` | 1 | concurrent ledger transactions |
| `--mode` | `correctness` | `correctness` or `throughput` |
| `--pause_ms MS` | 100 | pause between layers |
| `--disable_peer_stats` | off | skip peer CPU/memory sampling |
| `--fast_e2e` | off | shorter end-to-end run |
| `--save_check_charts` | off | also draw the charts described in `check.txt` |
| `--tps_latency_sweep` | off | TPS/latency sweep over `--tps_latency_rates` and `--endorser_counts` |
| `--tps_latency_rates` | `50,100,150,200,250` | rates for the sweep |
| `--endorser_counts` | `1,2,3` | endorser counts for the sweep |
| `--sweep_concurrency N` | 16 | concurrency for the sweep |

Layer 1 can also be run on its own: `python layer-1/generate_shares.py --genome /path/to/file.fna`.

## 4. Running the Layer-2 benchmark

Single configuration (all parties as local processes on one host):
```bash
cd layer-2
python smpc_bench.py -M 3 --k 10000 --trials 100 --warmup 10            # MPyC default field
python smpc_bench.py -M 3 --k 10000 --trials 100 --warmup 10 --bits 224 # SecInt(224): 256-bit prime field
```

Options: `--k` (vector length), `--trials`, `--warmup`, `--bits` (SecInt bit length; MPyC default is 32,
which gives a 64-bit prime; 224 gives a 256-bit prime), `--seed`, `--out-dir`, `--tag`. MPyC's own options
(`-M`, `-I`, `--ssl`, `-T`, ...) are passed through.

TLS between parties (`--ssl`): generate certificates first. They are written to `layer-2/.config/`, which
is git-ignored.
```bash
cd layer-2 && ./gen_certs.sh 16 && cd ..   # certificates for up to 16 parties
```

Grid runs and summaries:
```bash
python bench/run_grid.py --profile aligned   # --ssl, --bits 224, n in {3..8,12,16}, k in {10k,50k,100k}
python bench/run_grid.py --profile default   # MPyC defaults (no TLS, default field)
python bench/summarize.py aligned default    # -> results/smpc_summary_<profile>.csv
python bench/make_tables.py                  # Markdown tables from results/*.csv
python bench/preagg_bench.py                 # pre-aggregation timing on synthetic genotypes
python bench/run_original_smpc.py            # repeated runs of layer-2/layer2_smpc.py
```
`run_grid.py` accepts `--parties`, `--ks`, `--trials` and `--warmup` to change the grid.

Per trial, `smpc_bench.py` records on party 0: share generation and distribution (`t_sharing`), circuit
evaluation (`t_eval`), reconstruction (`t_recon`), online time (`t_online = t_eval + t_recon`), SHA-256
commitment (`t_hash`) and verification (`t_verify`).

## 5. Layer 3: Hyperledger Fabric setup

Clone `fabric-samples` into `layer-3/` at the commit used by this project and install the Fabric binaries
and Docker images:
```bash
git clone https://github.com/hyperledger/fabric-samples.git layer-3/fabric-samples
git -C layer-3/fabric-samples checkout 7f0f4a24fad0f27c952a7d8381d6f7fb4b737871
cd layer-3/fabric-samples
curl -sSLO https://raw.githubusercontent.com/hyperledger/fabric/main/scripts/install-fabric.sh
chmod +x install-fabric.sh
./install-fabric.sh --fabric-version 2.5.4 docker binary
```

Start the test network, create the channel and deploy the `basic` chaincode:
```bash
cd test-network
./network.sh up createChannel -c mychannel
./network.sh deployCC -ccn basic -ccp ../asset-transfer-basic/chaincode-go -ccl go
```

`automate_layers.py` expects `layer-3/fabric-samples/test-network/blockchain.py`, the `peer` binary in
`layer-3/fabric-samples/bin/`, peers at `localhost:7051` (Org1) and `localhost:9051` (Org2), optionally
`localhost:11051` (Org3), and the orderer at `localhost:7050`.

## 6. Threat model

The framework assumes a static, semi-honest adversary that corrupts fewer than half of the computing
parties (t < n/2). Shamir secret sharing in MPyC protects the pre-aggregated vectors; TLS, Fabric MSP
identities, Raft ordering and SHA-256 hash commitments are computational mechanisms. The Raft ordering
service is crash-fault-tolerant (CFT) and is trusted. Malicious parties, side channels and dynamic
membership are out of scope.

## 7. Results

Output files (summary CSVs, per-trial data, logs and per-party memory figures) are in
[`results/`](results/) and `results/raw/`.
