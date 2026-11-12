#!/usr/bin/env bash
# =====================================================================================================
# orchestrate_node2.sh — MDCOLAB-CHAIN AWS run (12 Nov 2026): replaces the Table II part of orchestrate_node.sh from
# 18:55 MYT (after F4RUN and F2's bs30 seq + rate50 at 16 workers). Runs on the Fabric node under nohup:
# G1, G2, G3, G0, G4, G5 (see aws_fabric.sh), network down, then schedules this node's own shutdown(=terminate) +150 min.
# Feeds Table II / Fig. 3.
# =====================================================================================================
cd /home/ubuntu; L=/home/ubuntu/orchestrate.log; log() { echo "[$(date '+%F %T %Z')] $*" >> $L; }
log "orchestrate_node2 START"
for G in G1 G2 G3 G0 G4 G5; do log "phase $G"; bash aws_fabric.sh $G >> $L 2>&1; done
bash aws_fabric.sh DOWN >> $L 2>&1; log ALL_DONE; sudo shutdown -c; sudo shutdown -h +150 "MDCOLAB post-run failsafe"; log "self shutdown scheduled +150 min"
