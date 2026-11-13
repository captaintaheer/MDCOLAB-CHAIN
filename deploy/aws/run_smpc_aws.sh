#!/usr/bin/env bash
# =====================================================================================================
# run_smpc_aws.sh — MDCOLAB-CHAIN AWS run (12 Nov 2026): multi-host online-SMPC benchmark.
# Feeds: Table I multi-node rows (n=8,k=10000; n=16,k=50000), and the
#   Section IV-B AWS party grid n in {4,8,12,16} x k in {10000,50000} (results/smpc_online/aws/nN_kK/).
# What it runs: the UNMODIFIED repo script layer-2/smpc_bench.py (fix/runnable 03f1599) as n separate MPyC
#   processes, one party per c6i.large node (nodes 0..n-1 of nodes.txt), all in one AZ and one cluster
#   placement group, connected over private IPs with MPyC's own options: -P host:port (once per party, same
#   list on every node) and -I <party index>. Default profile: MPyC default field (SecInt l=32 -> 64-bit prime),
#   no MPyC TLS, default threshold t=(n-1)//2, 100 trials after 10 warm-ups, seed 20261017.
#   Party 0 is wrapped by harness/runexp.py (writes run_meta.json, stdout/stderr); parties 1..n-1 log to partyI.log.
#   Every trial is checked on party 0 against an independent NumPy plaintext oracle (oracle_match column).
# Inputs: nodes.txt (index, instance id, public IP, private IP, AZ, PG) and the SSH key in this directory.
# Usage: run_smpc_aws.sh N K [TAGPREFIX]     e.g.  ./run_smpc_aws.sh 8 10000
# Output: results/smpc_online/aws/nN_kK/ : trials_<tag>.csv (party 0, per trial), mem_<tag>_p<i>.json (each party:
#   peak RSS, bytes sent), party logs, run_meta.json.
# =====================================================================================================
set -u; cd "${AWS_WORKDIR:-$(dirname "$0")}"
N=$1; K=$2; PFX=${3:-default}; TAG=${PFX}_n${N}_k${K}; PORT=11365
SSH="timeout 3700 ssh -o ServerAliveInterval=15 -i ${SSH_KEY:-mdcolab.pem} -o UserKnownHostsFile=known_hosts -o BatchMode=yes -o ConnectTimeout=15"
mapfile -t PUB < <(cut -f3 nodes.txt); mapfile -t PRIV < <(cut -f4 nodes.txt)
PL=""; for ((i=0;i<N;i++)); do PL="$PL -P ${PRIV[$i]}:$PORT"; done
OD=/home/ubuntu/run/out/smpc_aws/n${N}_k${K}
BENCH="cd /home/ubuntu/run/MDCOLAB-CHAIN/layer-2 && /home/ubuntu/venv/bin/python smpc_bench.py $PL --k $K --trials 100 --warmup 10 --seed 20261017 --tag $TAG --out-dir $OD"
for ((i=1;i<N;i++)); do
  $SSH ubuntu@${PUB[$i]} "mkdir -p $OD; nohup bash -c '$BENCH -I $i' > $OD/party$i.log 2>&1 &" &
done; wait
PARAMS="{\"profile\":\"default\",\"n\":$N,\"k\":$K,\"trials\":100,\"warmup\":10,\"bits\":null,\"ssl\":false,\"seed\":20261017,\"deployment\":\"one party per c6i.large node, cluster PG, ap-southeast-1a, MPyC -P host:port over private IPs\"}"
$SSH ubuntu@${PUB[0]} "mkdir -p $OD; cd /home/ubuntu/run && MDC_REPO=/home/ubuntu/run/MDCOLAB-CHAIN /home/ubuntu/venv/bin/python harness/runexp.py --dir $OD --id smpc-aws-default-n$N-k$K --maps 'Table I (multi-node rows)' --host 'aws ap-southeast-1a c6i.large x$N (one party per node, cluster placement group)' --params '$PARAMS' --timeout 3600 --cwd /home/ubuntu/run/MDCOLAB-CHAIN/layer-2 -- /home/ubuntu/venv/bin/python smpc_bench.py $PL --k $K --trials 100 --warmup 10 --seed 20261017 --tag $TAG --out-dir $OD -I 0"
L=results/smpc_online/aws/n${N}_k${K}; mkdir -p $L
for ((i=0;i<N;i++)); do
  for t in 1 2 3 4 5 6 7 8 9 10; do $SSH ubuntu@${PUB[$i]} "ls $OD/mem_${TAG}_p$i.json" >/dev/null 2>&1 && break; sleep 3; done
  timeout 120 scp -q -i ${SSH_KEY:-mdcolab.pem} -o UserKnownHostsFile=known_hosts -o ConnectTimeout=15 -o ServerAliveInterval=10 "ubuntu@${PUB[$i]}:$OD/*" $L/
done
echo "collected $(ls $L | wc -l) files into $L"; tail -2 $L/stdout.log
