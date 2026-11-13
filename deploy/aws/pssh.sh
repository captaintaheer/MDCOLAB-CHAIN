#!/usr/bin/env bash
# =====================================================================================================
# pssh.sh — MDCOLAB-CHAIN AWS run (12 Nov 2026): run one shell command on all SMPC nodes in parallel over SSH.
# Input: nodes.txt (index, instance id, public IP, private IP, AZ, placement group), SSH key in this directory.
# Used for node preparation and for the inter-node RTT measurement (results/aws_2026-11-12/env/rtt_ping_fullmesh.txt):
#   ./pssh.sh 'for h in <all private IPs>; do ping -q -c 20 -i 0.05 $h | tail -1; done'
# Feeds: .
# =====================================================================================================
# run a command on all SMPC nodes in parallel: pssh.sh 'cmd'
cd "${AWS_WORKDIR:-$(dirname "$0")}"
while read IDX IID PUB PRIV AZ PG; do
  ( ssh -i ${SSH_KEY:-mdcolab.pem} -o StrictHostKeyChecking=no -o UserKnownHostsFile=known_hosts -o ConnectTimeout=15 -o BatchMode=yes ubuntu@$PUB "$1" 2>&1 | sed "s/^/[$IDX] /" ) &
done < nodes.txt
wait
