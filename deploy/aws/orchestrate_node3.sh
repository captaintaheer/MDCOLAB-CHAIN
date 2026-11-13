#!/usr/bin/env bash
# orchestrate_node3.sh — re-run of Table II 3-org phases G4 (MAJORITY) and G5 (ANY) after fixing fabric_config.sh
# (Org3 chaincode install subshell inherited set -euo pipefail; the "queryinstalled | grep" check in fabric-samples ccutils.sh
# returns 1 when the package is not yet installed, which aborted the subshell). Same 64-worker protocol as G0. No self-shutdown change.
cd /home/ubuntu; L=/home/ubuntu/orchestrate.log; log() { echo "[$(date "+%F %T %Z")] $*" >> $L; }
log "orchestrate_node3 START (G4/G5 rerun)"
for G in G4 G5; do log "phase $G"; bash aws_fabric.sh $G >> $L 2>&1; done
bash aws_fabric.sh DOWN >> $L 2>&1; log ALL_DONE_3
