#!/usr/bin/env bash
# =====================================================================================================
# orchestrate_node.sh — MDCOLAB-CHAIN AWS run (12 Nov 2026): remaining run sequence, executed ON the Fabric node
# with nohup (independent of the orchestrating host). Order (priority Table III, then Table II):
#   1. (control-host-started runs n4_k10000, n4_k50000 kept; interrupted n4_k100000 and n8_k10000 moved to pipeline_aws_failed/) 2. Table III grid (stock Fabric, BT 2 s) remaining
#   configs + Table V-C t=1,2,3; 3. Fabric BT 0.2 s network + Table III grid on it; 4. shut down the SMPC nodes
#   (instance-initiated shutdown => terminate); 5. Table II: F4RUN (BT 0.2 s ledger), F2 (block size / ANY), F3 (3 orgs,
#   1-3 endorsers); network down; 6. schedule this node's own shutdown(=terminate) 150 min later as a failsafe
#   (results are pulled by the control host before then; teardown is done by cleanup.sh).
# =====================================================================================================
cd /home/ubuntu; L=/home/ubuntu/orchestrate.log
log() { echo "[$(date '+%F %T %Z')] $*" >> $L; }
log START
for NK in "4 100000" "8 10000" "8 50000" "8 100000" "12 10000" "12 50000" "16 10000" "16 50000"; do bash node_run_pipeline.sh $NK >> $L 2>&1; done
for T in 1 2 3; do bash node_run_pipeline.sh 8 10000 $T >> $L 2>&1; done
log "BT2s pipeline grid done"; bash aws_fabric.sh F4CFG >> $L 2>&1
export FABRIC_CFG_NAME=bs10_bt0.2s_endorseMAJORITY_orgs2
for NK in "4 10000" "4 50000" "4 100000" "8 10000" "8 50000" "8 100000" "12 10000" "12 50000" "16 10000" "16 50000"; do bash node_run_pipeline.sh $NK >> $L 2>&1; done
unset FABRIC_CFG_NAME; log "BT0.2s pipeline grid done; shutting down SMPC nodes"
for h in $(cut -f2 nodes_private.txt); do ssh -i /home/ubuntu/mdcolab.pem -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o LogLevel=ERROR -o ConnectTimeout=15 ubuntu@$h 'sudo shutdown -h now' ; done; log "SMPC nodes shutdown issued"
bash aws_fabric.sh F4RUN >> $L 2>&1; bash aws_fabric.sh F2 >> $L 2>&1; bash aws_fabric.sh F3 >> $L 2>&1; bash aws_fabric.sh DOWN >> $L 2>&1
log ALL_DONE; sudo shutdown -c; sudo shutdown -h +150 "MDCOLAB post-run failsafe" ; log "self shutdown scheduled +150 min"
