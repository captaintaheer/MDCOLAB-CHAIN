# Implementation status by layer

| Layer | Role | Status | Source |
|---|---|---|---|
| 1. Pre-aggregation and secret sharing | Each institution reduces its records to an allele-count vector and secret-shares it | Demonstrator scripts; the evaluation uses synthetic allele-count vectors generated inside the benchmark scripts, which secret-share them with `mpc.input` | `layer-1/generate_shares.py`, `layer-1/layer1_data_input.py`; synthetic generator in `layer-2/smpc_bench.py` and `harness/pipeline_bench.py` |
| 2. SMPC aggregation | MPyC (Shamir, semi-honest, t < n/2): r = sum of the party vectors, reconstruction | Implemented and evaluated | `layer-2/smpc_bench.py` (vector benchmark), `layer-2/layer2_smpc.py` and `layer-2/compute_sum.py` (original demonstrator), `harness/pipeline_bench.py` |
| 3. Permissioned ledger | SHA-256 commitment of the result, Fabric 2.5.4 commit and read-back | Implemented and evaluated | `harness/pipeline_bench.py` (`fabric_commit`), `harness/fabric_bench.py`, `harness/fabric_config.sh`, `automate_layers.py` (`collect_ledger_metrics`), `layer-3/blockchain.py`, `layer-3/README.md`; chaincode: `asset-transfer-basic` (Go) from fabric-samples 7f0f4a2 |
| 4. Dissemination and access control | Consent-aware delivery of results to authorised consumers; consent chaincode | Designed, not implemented | none in this repository |

## Layer 4

There is no Layer 4 code and no consent chaincode in this repository or its history. The ledger
uses the unmodified `asset-transfer-basic` chaincode, which stores the result digest as an asset;
it does not record consent state or enforce access decisions.

## Workloads

The evaluated workload is allele-count aggregation: each party holds a vector of k allele counts
and the parties compute their element-wise sum. No code for a case-control count aggregation
(separate case and control counts for a binary phenotype) exists in this repository or its
history (searched for `case`/`control`, `phenotype` and related terms in all branches).
