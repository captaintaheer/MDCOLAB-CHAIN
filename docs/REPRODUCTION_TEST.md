# Reproduction test in a fresh environment

Run on 12 Nov 2026 (UTC+8) on a Linux x86_64 machine with 8 CPUs, starting from a new clone of the
branch, a new virtual environment and only `requirements-lock.txt` installed. Docker was not
available on that machine, so steps that need a Fabric network were limited to the checks listed
below. The complete console output is in
[`reproduction_test_2026-11-12.log`](reproduction_test_2026-11-12.log).

## Commands

```bash
git clone --branch revision/jait23816-repro <repository> MDCOLAB-CHAIN && cd MDCOLAB-CHAIN
uv venv -p 3.12 .venv && . .venv/bin/activate        # or: python3.12 -m venv .venv
uv pip install -r requirements-lock.txt              # or: pip install -r requirements-lock.txt

# 1. online SMPC benchmark, 3 local parties
(cd layer-2 && python smpc_bench.py -M 3 --k 1000 --trials 5 --warmup 1 --seed 20261017 --tag demo_n3_k1000 --out-dir /tmp/out/smpc)
# 2. pipeline benchmark without the ledger step
python harness/pipeline_bench.py -M 3 --k 1000 --trials 5 --warmup 1 --seed 20261017 --tag demo_pipe --out-dir /tmp/out/pipe
# 3. integrity check tests
python -m unittest tests/test_integrity_readback.py -v
# 4. AWS tables and comparison with the reported values
(cd results/aws_2026-11-12 && python make_tables.py && git status --short . && python check_reported_values.py)
# 5. legacy x86 tables
MDCOLAB_RESULTS=results/legacy/x86_2026-10-17 python bench/make_tables.py
# 6. Layer 3 readiness without Fabric
python layer-3/blockchain.py
# 7. Figure 3 and tps.py (matplotlib)
uv pip install matplotlib
python results/aws_2026-11-12/make_fig3.py && bash tps.py && git status --short
```

## Results

| Step | Result |
|---|---|
| Environment | Python 3.12.15; installed packages exactly `mpyc==0.9`, `numpy==1.26.4`, `psutil==7.2.2` |
| 1. Online SMPC, n = 3, k = 1000 | Completed: `n=3 k=1000 p_bits=64 ssl=False online mean=1.039ms median=0.994 p95=1.391 match=5/5 peakRSS=49.2MB`; per-trial CSV and three per-party memory files written |
| 2. Pipeline without ledger | Completed: `n=3 t=1 k=1000 preagg=on N=5 pipeline mean=4.8ms online mean=1.192ms match=5/5 fabric_ok=0 verified=0 peakRSS_p0=42.0MB` (no Fabric step requested) |
| 3. Integrity tests | 3 tests, all passed |
| 4. AWS tables | `make_tables.py` rewrote all 9 table files with identical content (`git status` empty). `check_reported_values.py`: 112 of 113 values match; the difference is the upper end of the sharing range in the Table III footnote, reported as 1,105 ms while the data give 1104.46 ms (1,104 ms when rounded) |
| 5. Legacy tables | Printed from `results/legacy/x86_2026-10-17/` |
| 6. Layer 3 without Fabric | `layer-3/blockchain.py` exits 1 with "peer CLI not available"; `check_fabric()` lists the missing fabric-samples clone, peer binary and Docker |
| 7. Figure 3 and tps.py | `figures/fig3_fabric.png` rebuilt byte-identical to the committed file (`git status` empty); values 61.5 / 72.1 / 61.5 / 60.6 / 59.0 / 61.5 / 60.1 TPS. `tps.py` lists the missing Fabric prerequisites and draws its chart with zero values |

The timings of steps 1 and 2 are from a single shared machine with all parties as local
processes; they only show that the code runs and are not comparable with the AWS values.

## Integrity check before and after the change

The stub-peer scenario of `tests/test_integrity_readback.py` (four concurrent invokes in throughput
mode; the asset becomes readable after three queries) was run against `collect_ledger_metrics()`
of commit 03f1599 and of the current branch, three times each:

```
03f1599 (before): integrity_ok=False query_latency=0.0000 tx_success_rate=1.0 integrity_reason=(not recorded)
HEAD (after): integrity_ok=True query_latency=0.0219 tx_success_rate=1.0 integrity_reason=digest_match
03f1599 (before): integrity_ok=False query_latency=0.0000 tx_success_rate=1.0 integrity_reason=(not recorded)
HEAD (after): integrity_ok=True query_latency=0.0224 tx_success_rate=1.0 integrity_reason=digest_match
03f1599 (before): integrity_ok=False query_latency=0.0000 tx_success_rate=1.0 integrity_reason=(not recorded)
HEAD (after): integrity_ok=True query_latency=0.0214 tx_success_rate=1.0 integrity_reason=digest_match
```

The values before the change reproduce the pattern of the first metrics report
(`Integrity OK False`, `Query Latency 0.0`, `Tx Success Rate 1.0`).

## Not run in this test

* Fabric test-network, ledger commits and the AWS deployment: no Docker host was used, and no
  cloud resources were created. The ledger results come from the AWS run in
  `results/aws_2026-11-12/`.
* `automate_layers.py` end to end (needs Fabric and a FASTA input).
