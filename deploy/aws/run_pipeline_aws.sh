#!/usr/bin/env bash
# =====================================================================================================
# run_pipeline_aws.sh — MDCOLAB-CHAIN AWS run (12 Nov 2026): multi-host cryptographic-and-ledger pipeline.
# Feeds: Table III (pipeline latency / jobs/s / peak mem vs n,k) and, with T given, Table V-C (threshold).
# Deployment: party 0 runs on the Fabric node (c6i.2xlarge, Docker test-network, commits each result
#   hash with the peer CLI --waitForEvent and reads it back); parties 1..n-1 run one per c6i.large SMPC
#   node (SMPC nodes 0..n-2 in nodes.txt). MPyC over private IPs (-P host:port, -I index). No MPyC TLS.
# Code: harness/pipeline_bench.py (unchanged from the 2026-11-11 x86 re-run), 100 trials after 10 warm-ups,
#   seed 20261017, MPyC default field (64-bit prime), default threshold t=(n-1)//2 unless T given.
# Inputs: nodes.txt (index, instance id, public IP, private IP, AZ, PG), FABRIC_PRIV (Fabric node private IP),
#   FABRIC_PUB, SSH key. Usage: run_pipeline_aws.sh N K [T]
# Output: results/pipeline/aws/<fabric_config>/nN_kK[_tT]/ (trials CSV, per-party mem JSON, logs, run_meta.json)
# =====================================================================================================
set -u; cd "${AWS_WORKDIR:-$(dirname "$0")}"
N=$1; K=$2; T=${3:-}; PORT=11366
FPUB=${FABRIC_PUB:?}; FPRIV=${FABRIC_PRIV:?}; CFG=${FABRIC_CFG_NAME:-bs10_bt2s_endorseMAJORITY_orgs2}
SSH="timeout 3700 ssh -o ServerAliveInterval=15 -i ${SSH_KEY:-mdcolab.pem} -o UserKnownHostsFile=known_hosts -o BatchMode=yes -o ConnectTimeout=15"
mapfile -t PUB < <(cut -f3 nodes.txt); mapfile -t PRIV < <(cut -f4 nodes.txt)
HOSTS=("$FPRIV"); HPUB=("$FPUB"); for ((i=0;i<N-1;i++)); do HOSTS+=("${PRIV[$i]}"); HPUB+=("${PUB[$i]}"); done
PL=""; for ((i=0;i<N;i++)); do PL="$PL -P ${HOSTS[$i]}:$PORT"; done
SUF=""; TOPT=""; [ -n "$T" ] && { SUF="_t$T"; TOPT="-T $T"; }
TAG=pipeline_${CFG}_n${N}_k${K}${SUF}; OD=/home/ubuntu/run/out/pipeline_aws/$CFG/n${N}_k${K}${SUF}
ARGS="$PL $TOPT --k $K --trials 100 --warmup 10 --seed 20261017 --fabric --tag $TAG --out-dir $OD"
for ((i=1;i<N;i++)); do
  $SSH ubuntu@${HPUB[$i]} "mkdir -p $OD; cd /home/ubuntu/run/harness; nohup /home/ubuntu/venv/bin/python pipeline_bench.py $ARGS -I $i > $OD/party$i.log 2>&1 &" &
done; wait
PARAMS="{\"n\":$N,\"k\":$K,\"t\":\"${T:-MPyC default (n-1)//2}\",\"trials\":100,\"warmup\":10,\"bits\":null,\"ssl\":false,\"seed\":20261017,\"fabric_config\":\"$CFG\",\"deployment\":\"party 0 on Fabric node c6i.2xlarge; parties 1..n-1 one per c6i.large node; cluster PG ap-southeast-1a\"}"
$SSH ubuntu@$FPUB "mkdir -p $OD; cd /home/ubuntu/run && MDC_REPO=/home/ubuntu/run/MDCOLAB-CHAIN FABRIC_TEST_NETWORK=/home/ubuntu/run/MDCOLAB-CHAIN/layer-3/fabric-samples/test-network /home/ubuntu/venv/bin/python harness/runexp.py --dir $OD --id pipeline-aws-$CFG-n$N-k$K$SUF --maps 'Table III; Table V' --host 'aws ap-southeast-1a: party0 c6i.2xlarge (Fabric node) + $((N-1)) x c6i.large' --params '$PARAMS' --timeout 3600 --cwd /home/ubuntu/run/harness -- /home/ubuntu/venv/bin/python pipeline_bench.py $ARGS -I 0"
L=results/pipeline/aws/$CFG/n${N}_k${K}${SUF}; mkdir -p $L
for ((i=0;i<N;i++)); do
  for t in $(seq 1 10); do $SSH ubuntu@${HPUB[$i]} "ls $OD/mem_${TAG}_p$i.json" >/dev/null 2>&1 && break; sleep 3; done
  timeout 120 scp -q -i ${SSH_KEY:-mdcolab.pem} -o UserKnownHostsFile=known_hosts -o ConnectTimeout=15 -o ServerAliveInterval=10 "ubuntu@${HPUB[$i]}:$OD/*" $L/
done
echo "collected $(ls $L | wc -l) files into $L"; tail -1 $L/stdout.log
