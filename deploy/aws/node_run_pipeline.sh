#!/usr/bin/env bash
# =====================================================================================================
# node_run_pipeline.sh — MDCOLAB-CHAIN AWS run (12 Nov 2026): Table III / Table V-C pipeline runner, executed ON the
# Fabric node (moved there from the control host at ~17:10 MYT so that pauses of the orchestrating machine cannot
# interrupt a run). Party 0 = this node (Fabric commit + read-back via peer CLI); parties 1..n-1 = SMPC nodes
# 0..n-2 of nodes_private.txt (one party per c6i.large), reached over private IPs. MPyC -P host:port / -I index.
# Code: harness/pipeline_bench.py unchanged; 100 trials after 10 warm-ups; seed 20261017; default field; no MPyC TLS.
# Usage: node_run_pipeline.sh N K [T]  (env FABRIC_CFG_NAME selects the output folder / Fabric config label)
# Output: /home/ubuntu/run/out/pipeline_aws/<cfg>/nN_kK[_tT]/ on this node; other parties' mem/log files are copied back.
# =====================================================================================================
set -u; cd /home/ubuntu
N=$1; K=$2; T=${3:-}; PORT=11366; CFG=${FABRIC_CFG_NAME:-bs10_bt2s_endorseMAJORITY_orgs2}
ME=$(hostname -I | awk '{print $1}')
SSH="ssh -i /home/ubuntu/mdcolab.pem -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o LogLevel=ERROR -o BatchMode=yes -o ConnectTimeout=15"
mapfile -t PRIV < <(cut -f2 nodes_private.txt)
HOSTS=("$ME"); for ((i=0;i<N-1;i++)); do HOSTS+=("${PRIV[$i]}"); done
PL=""; for ((i=0;i<N;i++)); do PL="$PL -P ${HOSTS[$i]}:$PORT"; done
SUF=""; TOPT=""; [ -n "$T" ] && { SUF="_t$T"; TOPT="-T $T"; }
TAG=pipeline_${CFG}_n${N}_k${K}${SUF}; OD=/home/ubuntu/run/out/pipeline_aws/$CFG/n${N}_k${K}${SUF}; mkdir -p $OD
ARGS="$PL $TOPT --k $K --trials 100 --warmup 10 --seed 20261017 --fabric --tag $TAG --out-dir $OD"
for ((i=1;i<N;i++)); do
  $SSH ubuntu@${HOSTS[$i]} "mkdir -p $OD; cd /home/ubuntu/run/harness; nohup /home/ubuntu/venv/bin/python pipeline_bench.py $ARGS -I $i > $OD/party$i.log 2>&1 &" &
done; wait
PARAMS="{\"n\":$N,\"k\":$K,\"t\":\"${T:-MPyC default (n-1)//2}\",\"trials\":100,\"warmup\":10,\"bits\":null,\"ssl\":false,\"seed\":20261017,\"fabric_config\":\"$CFG\",\"deployment\":\"party 0 on Fabric node c6i.2xlarge; parties 1..n-1 one per c6i.large node; cluster PG ap-southeast-1a\"}"
cd /home/ubuntu/run && MDC_REPO=/home/ubuntu/run/MDCOLAB-CHAIN FABRIC_TEST_NETWORK=/home/ubuntu/run/MDCOLAB-CHAIN/layer-3/fabric-samples/test-network \
  /home/ubuntu/venv/bin/python harness/runexp.py --dir $OD --id pipeline-aws-$CFG-n$N-k$K$SUF --maps 'Table III; Table V' \
  --host "aws ap-southeast-1a: party0 c6i.2xlarge (Fabric node) + $((N-1)) x c6i.large" --params "$PARAMS" --timeout 3600 --cwd /home/ubuntu/run/harness \
  -- /home/ubuntu/venv/bin/python pipeline_bench.py $ARGS -I 0
sleep 3
for ((i=1;i<N;i++)); do timeout 60 scp -q -i /home/ubuntu/mdcolab.pem -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o LogLevel=ERROR "ubuntu@${HOSTS[$i]}:$OD/*" $OD/; done
echo "$TAG files=$(ls $OD | wc -l) $(tail -1 $OD/stdout.log)"
