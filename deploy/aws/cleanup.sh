#!/usr/bin/env bash
# =====================================================================================================
# cleanup.sh — MDCOLAB-CHAIN AWS run (12 Nov 2026): tag-scoped teardown (tag Project=MDCOLAB-CHAIN-JAIT23816,
# region ap-southeast-1). Terminates instances (waits until terminated), deregisters AMIs and deletes their
# snapshots, deletes volumes, EIPs, ENIs, key pairs, security groups and placement groups carrying the tag,
# and removes the local private key. Never touches untagged (pre-existing) resources. Safe to re-run.
# Feeds no table.
# =====================================================================================================
# Tag-scoped teardown of everything created for this project. Safe to re-run.
: "${AWS_DEFAULT_REGION:=ap-southeast-1}"; export AWS_DEFAULT_REGION   # requires the AWS CLI on PATH
P=${PROJECT_TAG:-MDCOLAB-CHAIN-JAIT23816}; F="Name=tag:Project,Values=$P"
IDS=$(aws ec2 describe-instances --filters $F Name=instance-state-name,Values=pending,running,stopping,stopped,shutting-down --query 'Reservations[].Instances[].InstanceId' --output text)
[ -n "$IDS" ] && aws ec2 terminate-instances --instance-ids $IDS >/dev/null && aws ec2 wait instance-terminated --instance-ids $IDS && echo "terminated $IDS"
for A in $(aws ec2 describe-images --owners self --filters $F --query 'Images[].ImageId' --output text); do
  SN=$(aws ec2 describe-images --image-ids $A --query 'Images[].BlockDeviceMappings[].Ebs.SnapshotId' --output text)
  aws ec2 deregister-image --image-id $A && echo "deregistered $A"
  for S in $SN; do aws ec2 delete-snapshot --snapshot-id $S && echo "deleted snapshot $S"; done
done
for S in $(aws ec2 describe-snapshots --owner-ids self --filters $F --query 'Snapshots[].SnapshotId' --output text); do aws ec2 delete-snapshot --snapshot-id $S && echo "deleted snapshot $S"; done
for V in $(aws ec2 describe-volumes --filters $F --query 'Volumes[].VolumeId' --output text); do aws ec2 delete-volume --volume-id $V && echo "deleted volume $V"; done
for E in $(aws ec2 describe-addresses --filters $F --query 'Addresses[].AllocationId' --output text); do aws ec2 release-address --allocation-id $E && echo "released $E"; done
for N in $(aws ec2 describe-network-interfaces --filters $F --query 'NetworkInterfaces[].NetworkInterfaceId' --output text); do aws ec2 delete-network-interface --network-interface-id $N && echo "deleted eni $N"; done
aws ec2 describe-key-pairs --filters $F --query 'KeyPairs[].KeyName' --output text | tr '\t' '\n' | while read K; do [ -n "$K" ] && aws ec2 delete-key-pair --key-name $K && echo "deleted key $K"; done
for G in $(aws ec2 describe-security-groups --filters $F --query 'SecurityGroups[].GroupId' --output text); do aws ec2 delete-security-group --group-id $G && echo "deleted sg $G"; done
for G in $(aws ec2 describe-placement-groups --filters $F --query 'PlacementGroups[].GroupName' --output text); do aws ec2 delete-placement-group --group-name $G && echo "deleted pg $G"; done
rm -f "${SSH_KEY:-mdcolab.pem}" && echo "local pem removed"
