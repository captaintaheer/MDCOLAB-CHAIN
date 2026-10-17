# MDCOLAB-CHAIN

Code accompanying the manuscript *"Empirical Validation, Regulatory Alignment and Design Lessons of a
Lightweight SMPC–Blockchain Framework for Genomic Privacy"* (JAIT-23816).

> **Status of this repository (verified on branch `fix/runnable`, 2026-10-17).** This README only states
> facts that were checked against the code or against runs on the branch. Items the authors still have to
> supply are marked **TODO (author)**. Raw measurements (per-trial CSVs, logs and summaries) are in
> [`results/`](results/).

## 1. What is in the repository

| Layer (paper) | Paper description | What the repository actually contains |
|---|---|---|
| 1. Pre-aggregation + secret sharing | f_pre maps each party's VCF partition to a k-dimensional allele-count vector, which is then Shamir-shared | `layer-1/generate_shares.py` computes **one scalar** (G+C count of a FASTA file) and splits it into 3 **additive** shares (`random.randint(1,10)`, not Shamir, not modular), written to `layer-2/Input-P{0,1,2}-0`. It also writes `layer-1/shares.json`, whose `"shares"` entries are **fresh random numbers** (`random.randint(1,20)`), not the shares. `layer-1/layer1_data_input.py` is an unused PoC (`secretsharing` package, hardcoded toy data). The FASTA `data/genome.fna` is not shipped. No VCF parsing, SNP panel or 1000 Genomes code exists. |
| 2. SMPC aggregation (MPyC) | n parties evaluate a linear circuit over Shamir-shared vectors | `layer-2/compute_sum.py` (called by the pipeline) sums the three additive shares **in plaintext** and writes `result.txt` and its SHA-256. `layer-2/layer2_smpc.py` is run separately for metrics: it sums the three numbers from `shares.json` as **public constants** (`mpc.SecInt()(x)`, no `mpc.input`), so no party inputs a secret. Before the `automate_layers.py` fix on `fix/runnable` it always ran with a single party (m=1). |
| 3. Fabric ledger | hash commitments on a Raft-ordered Fabric channel | `automate_layers.py` calls `layer-3/fabric-samples/test-network/blockchain.py` and the `peer` CLI (`CreateAsset` on the sample `basic` chaincode, hash stored in an asset field). `layer-3/fabric-samples` is a **gitlink** to upstream `hyperledger/fabric-samples` commit `7f0f4a24` (2025-07-28) with **no `.gitmodules`**, so it is empty after cloning, and `blockchain.py` exists nowhere in the repo. No chaincode, network configuration, or crypto material of the authors is included. |
| 4. Consent / dissemination | consent world-state and an access gateway | **Not implemented.** Layer 4 is designed but not evaluated (as the revised manuscript states). |

Other files: `automate_layers.py` (orchestrator and report or chart generator), `tps.py` (despite its name, a shell
heredoc that calls a broken `import  as al` line and points to a macOS path), `check.txt` (author notes listing
target figures; `automate_layers.py --save_check_charts` **plots these numbers instead of measurements**, see
the note at the top of `check.txt`), `metrics_report.md` (output of one earlier run; see the header in that file),
`venv/` and `__pycache__/` (committed by mistake, macOS/Python 3.12, contains no MPyC).

Added on `fix/runnable`: `requirements.txt`, `layer-2/smpc_bench.py` (paper-aligned vector benchmark),
`layer-2/gen_certs.sh` (TLS certificates for MPyC `--ssl`), `bench/` (grid runner, summariser,
pre-aggregation timing, runner for the unmodified `layer2_smpc.py`), `results/` (raw CSVs and logs).

## 2. Setup (verified)

```bash
# Python 3.12 is required: MPyC 0.9 needs numpy<2, which has no wheels for Python 3.13.
uv venv -p 3.12 venv                  # or: python3.12 -m venv venv
. venv/bin/activate
pip install -r requirements.txt         # mpyc==0.9, numpy<2 (1.26.4 used), psutil, matplotlib
```
`gmpy2` was **not** installed for the measurements reported here (MPyC prints "Install package gmpy2 for
better performance"). TODO (author): state whether gmpy2 was installed for the paper's runs.

## 3. Running

Original pipeline (Layers 1–2 and the SMPC side metric; Layer 3 needs Fabric, see §6):
```bash
python automate_layers.py --genome data/<file>.fna --allow_multi_smpc --smpc_parties 3 \
       --report_path results/raw/my_report.md
```
Without `--allow_multi_smpc`, `layer2_smpc.py` runs with **one party** (`automate_layers.py:801`).

Paper-aligned Layer-2 benchmark (each party inputs a private k-vector, Shamir sharing, NumPy oracle):
```bash
cd layer-2 && ./gen_certs.sh 16 && cd ..             # TLS certificates (git-ignored)
python bench/run_grid.py --profile aligned           # 256-bit prime, --ssl, n∈{3..8,12,16}, k∈{10k,50k,100k}, N=100 after 10 warm-ups
python bench/run_grid.py --profile default           # MPyC defaults (64-bit prime, no TLS)
python bench/summarize.py aligned default            # -> results/smpc_summary_*.csv
python bench/preagg_bench.py                         # synthetic pre-aggregation timing
python bench/run_original_smpc.py                    # the unmodified layer2_smpc.py, for comparison
```

## 4. MPyC configuration facts (verified)

* MPyC version: **0.9** (the version named in the paper). The paper's numbers cannot be tied to a version
  from the repo: the committed `venv/` does not contain MPyC. TODO (author): confirm the version used.
* Field: `mpc.SecInt()` uses the default bit length l=32, giving the prime field
  **p = 9223372036854775907 (64 bits)** in MPyC 0.9 (MPyC 0.10/0.11: p = 18446744073709551427, also 64 bits).
  **No MPyC version uses a 256-bit prime by default**, so the paper's statement "MPyC 0.9.x default secint
  256-bit prime" does not match the code (`layer2_smpc.py:24`, `mpc.SecInt()`). (MPyC's REPL predefines
  `secfld256 = mpc.SecFld(2**8)`, which is GF(256), a field with 256 *elements*.) The aligned benchmark uses
  `SecInt(224)`, whose modulus is the 256-bit prime
  57896044618658097711785492504343953926634992332820282019728792003956564820063.
* Threshold: MPyC default t = ⌊(n−1)/2⌋. The original code never sets `-T`.
* TLS: **off** in all original code (no `--ssl` anywhere, no certificates in the repo). MPyC's `--ssl`
  needs `.config/party_<i>.crt/.key` and `.config/mpyc_ca.crt` (`layer-2/gen_certs.sh` creates them).
  With `--ssl`, Python's `ssl` default context (OpenSSL 3.5 on the test machine) is used; mutual
  certificate verification is required (`CERT_REQUIRED`). TODO (author): state whether `--ssl` was on in the paper's runs.
* Parties: all parties run as local processes on one host (`-M n` without `-I` spawns them).

## 5. Timing: what is measured

Original `layer-2/layer2_smpc.py` (unchanged, commit `8695ca4`):
```python
16      start_time = time.perf_counter()
18      await mpc.start()
 ...
27      for _ in range(args.num_ops):
28          result = sum(inputs)
29          results.append(await mpc.output(result))
 ...
40      await mpc.shutdown()
42      end_time = time.perf_counter()
43      execution_time = end_time - start_time
```
It **does** await `mpc.output`, but the window also includes `mpc.start()` (connection setup), reading
`shares.json`, `num_ops` (default 5) outputs, and `mpc.shutdown()`. It is one sample per process and has no
warm-up. The input is 3 scalars, not a k-vector. It is **not** the online-phase timer the paper describes.

Aligned harness `layer-2/smpc_bench.py` (party 0's clock; parties synchronised before each trial):
```python
68      t0 = time.perf_counter()
69-70   x = [mpc.input(sec.array(v if i == pid else dummy), senders=i) for i in range(m)]
71      await mpc.gather(x)                 # all shares held locally
72      t1 = time.perf_counter()            # -> t_sharing = t1 - t0  (share generation + distribution)
73-76   r = x[0] + x[1] + ... ; await mpc.gather(r)
77      t2 = time.perf_counter()            # -> t_eval
78      out = await mpc.output(r)           # reconstruction
79      t3 = time.perf_counter()            # -> t_recon; t_online = t3 - t1 (paper's definition)
84/86   t4/t5: SHA-256 commitment h = SHA-256(enc(r) || enc(meta)) and consumer-side re-verification
```

### Per-stage pipeline definition used for `results/`
`share generation + distribution` (t_sharing) → `online evaluation` (t_eval) → `reconstruction` (t_recon)
→ `hash commitment` (t_hash) → **Fabric commit (not measurable here)** → `verification` (t_verify).
MPyC's `mpc.input` generates and sends shares in one call, so generation and distribution cannot be timed
separately without changing MPyC. Local pre-aggregation (f_pre) is timed separately on synthetic genotypes
(`bench/preagg_bench.py`). TODO (author): the paper's Table III stage boundaries, and the code that produced them.

## 6. Hyperledger Fabric (Layer 3): what is needed, and what is unknown

Running Layer 3 requires Docker, `fabric-samples` with the Fabric binaries (`bin/peer`, `config/`), a running
`test-network` with channel `mychannel`, the `basic` chaincode deployed, and the missing
`layer-3/fabric-samples/test-network/blockchain.py`. The code assumes 2 orgs (peer0.org1:7051, peer0.org2:9051,
optional org3:11051) and one orderer at `localhost:7050`. These match the stock `test-network`. At the
gitlinked commit `7f0f4a24`, upstream `test-network/configtx/configtx.yaml` sets one `etcdraft` consenter,
`BatchTimeout: 2s`, `MaxMessageCount: 10`, `AbsoluteMaxBytes: 99 MB`, `PreferredMaxBytes: 512 KB`, and the
`MAJORITY Endorsement` channel policy (checked against upstream on 2026-10-17). Whether the authors changed
these values is unknown, so they **cannot be assumed** to be the paper's configuration. The code
measures latency per transaction as the wall time of the `peer chaincode invoke --waitForEvent` CLI call
plus polling `ReadAsset` until the hash appears (`automate_layers.py:288-313`).
TPS is computed as successes divided by batch wall time, with a thread pool of CLI calls (`:325-343`).

The paper's multi-node configuration is **not in the repository**. TODO (author), all required by Reviewer 2 Comment 2:
- Fabric version (thesis mentions 2.5.4: confirm), number of orgs and peers per org, number of Raft orderers
- `BatchTimeout`, `MaxMessageCount` (paper mentions 20–30 tx blocks), `AbsoluteMaxBytes`, `PreferredMaxBytes`
- endorsement policy used for 0.36 s (paper: "majority"), and the policies behind ">60 TPS (relaxed)"
- state database (LevelDB or CouchDB), chaincode name/language, and how h is stored
- instance types, vCPU/CPU model, RAM, placement (same AZ), RTT
- load generator (Caliper? the `peer` CLI thread pool in `automate_layers.py`?), offered load (tx/s), run
  duration, transaction count behind 42.86 TPS
- raw per-transaction finality logs (for median/p95/p99/SD)

## 7. Datasets

* The paper uses 1000 Genomes NYGC high-coverage data (2,504 unrelated samples) and simulated biobank
  matrices. **No dataset, download script, SNP-panel selection, partitioning or simulation code is in the repo.**
  The only data input in the code is a FASTA file for a single GC count.
* The aligned benchmark uses **synthetic** allele counts: Binomial(2·n_i, af) with af ~ U(0.01, 0.5), for 2,504
  samples split by sample-id mod n, seeded (`smpc_bench.py:46-50`). This exercises the arithmetic only.
* TODO (author): VCF release and build; chromosomes; SNP-panel filters (MAF, call rate, HWE, LD pruning or random);
  partition rule (manuscript says "sample ID mod n [A: confirm]"); simulated-matrix generator (individuals,
  AF source, genotype model, seed, software); scripts for each.
* TODO (author): independent validation of f_pre against `bcftools +fill-tags`/`bcftools query` or
  `plink2 --freq counts` on the raw VCFs (Reviewer 2 Comment 4.5). Not possible here: no VCFs, and no
  bcftools or PLINK installed.
* "Pre-aggregation off" (Table V: 6.8 s, 420 MB): **no code for this condition exists in the repo.**
  TODO (author): define what is shared in that condition and why it fits in 420 MB.

## 8. Reproducing each table and figure

| Paper item | Script in repo | Status |
|---|---|---|
| Table I (online SMPC, memory) | none originally; now `bench/run_grid.py` + `bench/summarize.py` | re-measured on this branch (x86 VM, synthetic inputs) |
| Fig. 2 (time/memory vs k, incl. k=25,000) | none | k=25,000 not run; TODO (author) |
| Table II, Fig. 3 (Fabric finality/TPS vs block size/policy) | `automate_layers.py` ledger functions (needs Fabric) | cannot run here (no Docker); multi-node config missing |
| Table III (pipeline vs n,k) | none (`automate_layers.py` has no k and no n>3 Layer-1 shares) | SMPC stages re-measured; Fabric stage missing |
| Table V (pre-agg on/off, threshold t) | none | not reproducible from the repo |
| 200-trial correctness | none originally; per-trial NumPy oracle in `smpc_bench.py` | re-measured |
| Charts in `metrics_report.md` "Publication Figures" | `save_check_charts()` | built from `check.txt` target values, not measurements |

## 9. Threat model (as stated in the revised manuscript; not something code can verify)

Static, semi-honest adversary corrupting t < n/2 parties (MPyC supports only t < n/2). Information-theoretic
privacy applies only to the Shamir shares of pre-aggregated vectors. TLS, Fabric MSP identities, Raft ordering
and SHA-256 are computational mechanisms. Raft is crash-fault-tolerant, not Byzantine-fault-tolerant: the
ordering service is trusted, and "tamper-evident" assumes uncompromised orderers, no colluding endorser quorum
and no leaked keys. Malicious parties, side channels and dynamic membership are out of scope. Layer 4 (consent
gateway) is designed but not implemented or evaluated. Released exact counts carry membership-inference risk.

## 10. Raw data and logs

All measurements from this branch are in `results/` (summary CSVs) and `results/raw/` (per-run logs,
per-party memory JSON). TODO (author): archive the original per-trial logs behind the paper's tables (the
manuscript says they exist; none are in the repo).
