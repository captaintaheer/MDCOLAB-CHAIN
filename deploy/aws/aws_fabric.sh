#!/usr/bin/env bash
# =====================================================================================================
# aws_fabric.sh — MDCOLAB-CHAIN AWS run (12 Nov 2026): Fabric 2.5.4 ledger benchmark driver (Table II, Fig. 3),
# adapted from the phase-2 Fabric driver used for the 11 Nov 2026 x86 re-run. Runs ON the Fabric node
# (c6i.2xlarge, Docker test-network: 1 Raft orderer, one peer per org, LevelDB, TLS on, asset-transfer-basic Go).
# For each configuration: harness/fabric_config.sh recreates the network with BatchTimeout / MaxMessageCount /
# org count / endorsement policy and snapshots the effective channel config; then harness/fabric_bench.py:
#   seq  : 100 sequential CreateAsset invokes, --waitForEvent (low-load finality)
#   rateR: open-loop offered load R in {50,100,150,200,250} tx/s for 60 s, 16 client workers (peer CLI)
# Phases: F1 = stock (BT 2s, MMC 10, 2 orgs, MAJORITY) + seq;  F1R = its rate sweep;
#   F2 = MMC 30/50 MAJORITY and MMC 10/30/50 ANY (1-of-n);  F3 = 3 orgs MAJORITY (2 and 3 endorsers) and
#   3 orgs ANY with 1/2/3 endorsers (the "1-3 endorsers" sweep);  F4CFG/F4RUN = BatchTimeout 0.2 s, MMC 10, MAJORITY
#   (network created first so the Table III pipeline could also run on it); DOWN = network.sh down.
#   G0-G5 (from 18:55 MYT): the same grid with 64 client workers (rate dirs suffixed _c64). With 16 workers each waiting for
#   its commit event, at most 16 txs are ever pending, so 30- and 50-tx blocks never fill and every block waits BatchTimeout
#   (bs30 rate50 at c16 took 412 s for 3000 txs). G1 bs30 MAJ, G2 bs50 MAJ, G3 bs10/30/50 ANY, G0 stock config at c64
#   (comparability), G4 3 orgs MAJ (2 and 3 endorsers), G5 3 orgs ANY (1/2/3 endorsers).
# Inputs: RUN_ROOT (default /home/ubuntu/run) holding MDCOLAB-CHAIN/ and harness/. Usage: aws_fabric.sh F1|F1R|F2|F3|F4
# Output: run/out/fabric/<config>/{seq_eE,rateR_eE}/ (tx_log.csv, resources.csv, summary.json, run_meta.json)
#   and run/out/fabric_configs/<config>/ (configtx.diff, effective_channel_config.json, chaincode_definition.json).
# =====================================================================================================
set -u
R=${RUN_ROOT:-/home/ubuntu/run}; REPO=$R/MDCOLAB-CHAIN; H=$R/harness; O=$R/out
export MDC_REPO=$REPO FABRIC_TEST_NETWORK=$REPO/layer-3/fabric-samples/test-network
. /home/ubuntu/venv/bin/activate
HOSTLBL="aws ap-southeast-1a c6i.2xlarge (8 vCPU, 16 GiB), single instance running the Docker test-network"
RX="python $H/runexp.py --host"
mkdir -p $O/fabric_configs
cfg() { echo "[$(date '+%F %T %Z')] config $5"; $H/fabric_config.sh $1 $2 $3 $4 $O/fabric_configs/$5 > $O/fabric_configs/$5.setup.log 2>&1 || { echo "CONFIG FAILED $5"; return 1; }; }
pj() { echo "{\"block_size_MaxMessageCount\":$2,\"BatchTimeout\":\"$1\",\"orgs\":$3,\"endorsement_policy\":\"$4\",\"endorsers\":$6,\"rate\":$7,\"concurrency\":$8,\"duration_s\":$9,\"txs\":${10}}"; }
seqrun() { # BT MMC ORGS POL NAME E
  python $H/runexp.py --host "$HOSTLBL" --dir $O/fabric/$5/seq_e$6 --id fabric-$5-seq-e$6 --maps "Table II (finality); Fig. 3" --params "$(pj $1 $2 $3 $4 $5 $6 0 1 null 100)" \
     -- python $H/fabric_bench.py --rate 0 --txs 100 --endorsers $6 --out-dir $O/fabric/$5/seq_e$6 --tag ${5}_seq_e$6; }
rates() { # BT MMC ORGS POL NAME E [CONC]   (CONC default 16 = x86 harness / repo sweep; 64 used from 18:55 MYT)
  local C=${7:-16}; local S=""; [ "$C" != 16 ] && S="_c$C"
  for RATE in 50 100 150 200 250; do
    python $H/runexp.py --host "$HOSTLBL" --dir $O/fabric/$5/rate${RATE}_e$6$S --id fabric-$5-rate$RATE-e$6$S --maps "Table II (TPS); Fig. 3" --params "$(pj $1 $2 $3 $4 $5 $6 $RATE $C 60 null)" \
       -- python $H/fabric_bench.py --rate $RATE --duration 60 --concurrency $C --endorsers $6 --out-dir $O/fabric/$5/rate${RATE}_e$6$S --tag ${5}_r${RATE}_e$6$S
  done; }
case $1 in
F1) N=bs10_bt2s_endorseMAJORITY_orgs2; cfg 2s 10 2 majority $N && seqrun 2s 10 2 majority $N 2 ;;
F1R) N=bs10_bt2s_endorseMAJORITY_orgs2; rates 2s 10 2 majority $N 2 ;;
F2) for MMC in 30 50; do N=bs${MMC}_bt2s_endorseMAJORITY_orgs2; cfg 2s $MMC 2 majority $N && { seqrun 2s $MMC 2 majority $N 2; rates 2s $MMC 2 majority $N 2; }; done
    for MMC in 10 30 50; do N=bs${MMC}_bt2s_endorseANY_orgs2; cfg 2s $MMC 2 any $N && { seqrun 2s $MMC 2 any $N 1; rates 2s $MMC 2 any $N 1; }; done ;;
F3) N=bs10_bt2s_endorseMAJORITY_orgs3; cfg 2s 10 3 majority $N && { seqrun 2s 10 3 majority $N 2; seqrun 2s 10 3 majority $N 3; rates 2s 10 3 majority $N 2; rates 2s 10 3 majority $N 3; }
    N=bs10_bt2s_endorseANY_orgs3; cfg 2s 10 3 any $N && { for E in 1 2 3; do rates 2s 10 3 any $N $E; done; } ;;
F4CFG) N=bs10_bt0.2s_endorseMAJORITY_orgs2; cfg 200ms 10 2 majority $N ;;
F4RUN) N=bs10_bt0.2s_endorseMAJORITY_orgs2; seqrun 200ms 10 2 majority $N 2; rates 200ms 10 2 majority $N 2 ;;
G1) N=bs30_bt2s_endorseMAJORITY_orgs2; cfg 2s 30 2 majority $N && rates 2s 30 2 majority $N 2 64 ;;
G2) N=bs50_bt2s_endorseMAJORITY_orgs2; cfg 2s 50 2 majority $N && { seqrun 2s 50 2 majority $N 2; rates 2s 50 2 majority $N 2 64; } ;;
G3) for MMC in 10 30 50; do N=bs${MMC}_bt2s_endorseANY_orgs2; cfg 2s $MMC 2 any $N && { seqrun 2s $MMC 2 any $N 1; rates 2s $MMC 2 any $N 1 64; }; done ;;
G0) N=bs10_bt2s_endorseMAJORITY_orgs2; cp -r $O/fabric_configs/$N $O/fabric_configs/${N}_first_network 2>/dev/null; cfg 2s 10 2 majority $N && rates 2s 10 2 majority $N 2 64 ;;
G4) N=bs10_bt2s_endorseMAJORITY_orgs3; cfg 2s 10 3 majority $N && { seqrun 2s 10 3 majority $N 2; seqrun 2s 10 3 majority $N 3; rates 2s 10 3 majority $N 2 64; rates 2s 10 3 majority $N 3 64; } ;;
G5) N=bs10_bt2s_endorseANY_orgs3; cfg 2s 10 3 any $N && { for E in 1 2 3; do rates 2s 10 3 any $N $E 64; done; } ;;
DOWN) cd $FABRIC_TEST_NETWORK && PATH=$PWD/../bin:$PATH ./network.sh down > $O/fabric_configs/final_down.log 2>&1 ;;
esac
echo "PHASE_$1_DONE $(date '+%F %T %Z')"
