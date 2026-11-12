# MDCOLAB-CHAIN

Code, benchmark harness and results for *"Empirical Validation, Regulatory Alignment and Design
Lessons from a Lightweight SMPC–Blockchain Framework for Genomic Privacy"*.

MDCOLAB-CHAIN aggregates allele-count vectors held by several institutions with secure multi-party
computation (MPyC, Shamir secret sharing) and records a SHA-256 commitment of each result on a
permissioned ledger (Hyperledger Fabric), where consumers can read it back and verify it.

## Contents

| Path | Contents |
|---|---|
| `layer-1/` | Layer 1 demonstrator: input preparation and secret sharing |
| `layer-2/` | Layer 2: MPyC aggregation; `smpc_bench.py` is the online SMPC benchmark |
| `layer-3/` | Layer 3: Fabric setup notes and `blockchain.py` readiness check |
| `harness/` | Pipeline benchmark, Fabric load generator, Fabric configuration script ([README](harness/README.md)) |
| `deploy/aws/` | Scripts and topology of the AWS run ([README](deploy/aws/README.md)) |
| `deploy/fabric-samples-local.diff` | Local change to the fabric-samples working copy used on AWS |
| `results/aws_2026-11-12/` | Raw data, logs and environment records of the AWS run, with the scripts that build every AWS table and Figure 3 ([README](results/aws_2026-11-12/README.md)) |
| `results/legacy/` | Earlier outputs kept for traceability, not used for the reported tables ([README](results/legacy/README.md)) |
| `automate_layers.py` | End-to-end demonstrator that runs Layers 1 to 3 and writes a metrics report |
| `bench/` | Single-host benchmark grid scripts |
| `tests/` | Unit tests (ledger read-back integrity check) |
| `docs/` | Table and figure manifest, per-stage results, reconciliation notes, layer status, reproduction test |

## Implementation status

| Layer | Status |
|---|---|
| 1. Pre-aggregation and secret sharing | Demonstrator; the benchmarks generate synthetic allele-count vectors and secret-share them with MPyC |
| 2. SMPC aggregation | Implemented and evaluated |
| 3. Permissioned ledger | Implemented and evaluated |
| 4. Dissemination and access control | Designed, not implemented |

Details and source paths: [docs/LAYER4_STATUS.md](docs/LAYER4_STATUS.md).

## Versions

| Component | Version |
|---|---|
| Python | 3.12 (MPyC 0.9 needs `numpy<2`); AWS nodes: 3.12.3 |
| Python packages | `requirements-lock.txt`: mpyc 0.9, numpy 1.26.4, psutil 7.2.2 (as installed on the AWS nodes); matplotlib (any recent version) only for charts |
| Hyperledger Fabric | 2.5.4 (peer, orderer, binaries), fabric-ca 1.5.17 |
| fabric-samples | commit 7f0f4a24fad0f27c952a7d8381d6f7fb4b737871, with `deploy/fabric-samples-local.diff` |
| Chaincode | `asset-transfer-basic` (Go) from fabric-samples |
| Docker | docker-ce 28.5.2 with the compose plugin (AWS Fabric node) |
| Go | 1.22.2 (chaincode vendoring by `network.sh deployCC`) |

## Installation

```bash
git clone https://github.com/captaintaheer/MDCOLAB-CHAIN.git && cd MDCOLAB-CHAIN
python3.12 -m venv .venv && . .venv/bin/activate      # or: uv venv -p 3.12 .venv
pip install -r requirements-lock.txt
pip install matplotlib                                # optional, for charts and Figure 3
python -m unittest tests/test_integrity_readback.py   # quick check, no Fabric needed
```

Fabric (needed for ledger runs only):

```bash
git clone https://github.com/hyperledger/fabric-samples.git layer-3/fabric-samples
git -C layer-3/fabric-samples checkout 7f0f4a24fad0f27c952a7d8381d6f7fb4b737871
git -C layer-3/fabric-samples apply ../../deploy/fabric-samples-local.diff
cd layer-3/fabric-samples
curl -sSLO https://raw.githubusercontent.com/hyperledger/fabric/main/scripts/install-fabric.sh
chmod +x install-fabric.sh && ./install-fabric.sh --fabric-version 2.5.4 docker binary
cd test-network
./network.sh up createChannel -c mychannel
./network.sh deployCC -ccn basic -ccp ../asset-transfer-basic/chaincode-go -ccl go
cd ../../..
export FABRIC_TEST_NETWORK=$PWD/layer-3/fabric-samples/test-network
```

`harness/fabric_config.sh` recreates the network with a given BatchTimeout, block size
(MaxMessageCount), organisation count and endorsement policy (see [harness/README.md](harness/README.md)).

## Running the experiments

All benchmarks use seed 20261017 and 100 timed trials after 10 warm-ups. Every party is started
with the same command and its own index `-I i`; `-P host:port` lists all parties in order
(MPyC options). For a single-host test, replace the `-P`/`-I` options with `-M n`.

| Experiment | Command (per party) | Used for |
|---|---|---|
| Online SMPC | `cd layer-2 && python smpc_bench.py -P h0:11365 ... -P h(n-1):11365 -I i --k K --trials 100 --warmup 10 --seed 20261017 --tag default_nN_kK --out-dir OUT` | Table I |
| Pipeline | `python harness/pipeline_bench.py -P fabric:11366 -P h1:11366 ... -I i [-T t] --k K --trials 100 --warmup 10 --seed 20261017 --fabric --tag TAG --out-dir OUT` (party 0 on the Fabric host) | Table III, Table V, stage breakdown |
| Fabric configuration | `harness/fabric_config.sh BT MMC ORGS POLICY SNAPSHOT_DIR`, e.g. `harness/fabric_config.sh 200ms 10 2 majority /tmp/cfg` | Table II, Table III |
| Fabric load | `python harness/fabric_bench.py --rate 0 --txs 100 --endorsers E --out-dir OUT --tag TAG` (sequential); `python harness/fabric_bench.py --rate R --duration 60 --concurrency C --endorsers E --out-dir OUT --tag TAG` | Table II, Figure 3 |

The AWS grid: n in {4, 8, 12, 16}, k in {10 000, 50 000} for online SMPC; n in {4, 8, 12, 16},
k in {10 000, 50 000, 100 000} (up to 50 000 for n = 12, 16) for the pipeline at BatchTimeout 0.2 s
and 2 s; t in {1, 2, 3} at n = 8, k = 10 000; Fabric: MaxMessageCount 10/30/50, majority and
1-of-n endorsement, 2 and 3 organisations, offered 50 to 250 tx/s with 16 or 64 clients. The
wrapper scripts are in [deploy/aws/](deploy/aws/).

Expected output of a small single-host run (values from the reproduction test; timings depend on
the machine):

```
$ cd layer-2 && python smpc_bench.py -M 3 --k 1000 --trials 5 --warmup 1 --seed 20261017 --tag demo_n3_k1000 --out-dir /tmp/out/smpc
... Start MPyC runtime v0.9
... All 3 parties connected.
n=3 k=1000 p_bits=64 ssl=False online mean=1.039ms median=0.994 p95=1.391 match=5/5 peakRSS=49.2MB

$ python harness/pipeline_bench.py -M 3 --k 1000 --trials 5 --warmup 1 --seed 20261017 --tag demo_pipe --out-dir /tmp/out/pipe
n=3 t=1 k=1000 preagg=on N=5 pipeline mean=4.8ms online mean=1.192ms match=5/5 fabric_ok=0 verified=0 peakRSS_p0=42.0MB
```

`match=5/5` is the comparison with the NumPy plaintext oracle; each run writes
`trials_<tag>.csv` (party 0) and `mem_<tag>_p<i>.json` (each party).

## AWS topology (run of 12 Nov 2026)

16 x c6i.large SMPC nodes (one MPyC party per node) and 1 x c6i.2xlarge Fabric node (Docker
test-network: one Raft orderer, one peer per organisation, LevelDB, TLS; also party 0 of the
pipeline runs), all in ap-southeast-1a in one cluster placement group, communicating over private
IPs (measured RTT 0.151 ms between SMPC nodes, 0.244 ms to the Fabric node). Ubuntu 24.04.5 LTS.
MPyC default field (64-bit prime), MPyC TLS off, threshold t = (n-1)//2 unless set with `-T`.
Full description: [deploy/aws/README.md](deploy/aws/README.md) and
[results/aws_2026-11-12/README.md](results/aws_2026-11-12/README.md).

## Rebuilding the tables and figures

```bash
cd results/aws_2026-11-12
python make_tables.py              # every AWS table, from the raw per-trial and per-transaction files
python check_reported_values.py    # compares the reported values with the rebuilt tables
python make_fig3.py                # Figure 3
```

[docs/MANIFEST.md](docs/MANIFEST.md) maps each table and figure to its script, output file and raw
data. [docs/PIPELINE_STAGES.md](docs/PIPELINE_STAGES.md) gives the per-stage pipeline times for
every (n, k). [docs/REPRODUCTION_TEST.md](docs/REPRODUCTION_TEST.md) records a run of these steps
in a new environment.

## End-to-end demonstrator

`automate_layers.py` runs Layers 1 to 3 in sequence and writes a Markdown report with charts:

```bash
python automate_layers.py --genome data/<file>.fna --allow_multi_smpc --smpc_parties 3 --report_path output/report.md
```

| Flag | Default | Meaning |
|---|---|---|
| `--genome PATH` | `data/genome.fna` | FASTA input for Layer 1 |
| `--report_path PATH` | `metrics_report.md` | where the report is written |
| `--allow_multi_smpc` | off | run `layer2_smpc.py` with `--smpc_parties` parties (otherwise one party) |
| `--smpc_parties N` | 3 | number of MPyC parties |
| `--smpc_ops N` | 5 | number of secure operations per SMPC run |
| `--smpc_python PATH` | auto | Python interpreter with MPyC installed |
| `--smpc_timeout_s S` | 10 | timeout for the SMPC metrics run |
| `--ledger_txs N` | 3 | number of ledger transactions |
| `--ledger_concurrency N` | 1 | concurrent ledger transactions (throughput mode) |
| `--mode` | `correctness` | `correctness` (each invoke waits for its commit) or `throughput` |
| `--pause_ms MS` | 100 | pause between layers |
| `--disable_peer_stats` | off | skip peer CPU/memory sampling |
| `--fast_e2e` | off | shorter end-to-end run |
| `--save_check_charts` | off | also draw the comparison charts defined in `check.txt` |
| `--tps_latency_sweep` | off | TPS/latency sweep over `--tps_latency_rates` and `--endorser_counts` |

`READBACK_TIMEOUT_S` (default 15) sets how long the final read-back waits for the last asset to be
committed ([docs/INTEGRITY_CHECK.md](docs/INTEGRITY_CHECK.md)). `bash tps.py` runs the TPS/latency
sweep and chart on its own. The values in the first report of this script are explained in
[docs/RECONCILIATION.md](docs/RECONCILIATION.md).

## Threat model

Static, semi-honest adversary corrupting fewer than half of the computing parties (t < n/2).
Shamir secret sharing in MPyC protects the pre-aggregated vectors; TLS, Fabric MSP identities, Raft
ordering and SHA-256 commitments are computational mechanisms. The Raft ordering service is
crash-fault-tolerant and trusted. Malicious parties, side channels and dynamic membership are out of
scope.
