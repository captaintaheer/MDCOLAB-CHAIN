# AWS deployment scripts (run of 12 Nov 2026)

These are the scripts used for the AWS run whose data is in
[`results/aws_2026-11-12/`](../../results/aws_2026-11-12/). Local paths and the SSH key name are
parameters; the node-side layout (`/home/ubuntu/run`, `/home/ubuntu/venv`) is that of the Ubuntu
AMI used. Running them creates billable AWS resources.

## Topology

| Item | Value |
|---|---|
| Region / AZ | ap-southeast-1, ap-southeast-1a (AZ id apse1-az2), all instances |
| Placement | one cluster placement group holding all 17 instances |
| Network | default VPC, one subnet, one security group (all traffic allowed inside the group, SSH from outside with a key only); all MPyC and Fabric traffic over private IPs |
| SMPC nodes | 16 x c6i.large (2 vCPU, 4 GiB, Intel Xeon Platinum 8375C), one MPyC party per node |
| Fabric node | 1 x c6i.2xlarge (8 vCPU, 16 GiB), Docker test-network (1 Raft orderer, one peer per org, LevelDB, TLS); also MPyC party 0 for the pipeline runs |
| OS | Ubuntu 24.04.5 LTS (ami-063d94c44d4eba6e0, Canonical), kernel 7.0.0-1014-aws |
| Software | Python 3.12.3, mpyc 0.9, numpy 1.26.4, psutil 7.2.2; Fabric 2.5.4, fabric-ca 1.5.17, fabric-samples 7f0f4a2; docker-ce 28.5.2 with compose plugin; go 1.22.2 |
| Measured RTT | SMPC to SMPC mean 0.151 ms, SMPC to Fabric node mean 0.244 ms (`results/aws_2026-11-12/env/rtt_ping_fullmesh.txt`) |

## Order of operations

1. Launch the Fabric node (c6i.2xlarge) with `userdata.sh` as user data and
   `--instance-initiated-shutdown-behavior terminate`, in the cluster placement group.
2. Copy a payload (`MDCOLAB-CHAIN/` without venv/results/certificates, plus `harness/`) to
   `/home/ubuntu/payload.tgz` and run `setup_node.sh` on it.
3. Create an AMI from that node and launch the 16 c6i.large SMPC nodes from it (same placement
   group, same `userdata.sh`).
4. On the Fabric node, replace Ubuntu's `docker.io` with docker-ce 28.5.2 and install `golang-go`
   (the Fabric 2.5.4 chaincode build failed with docker.io 29.1.3, whose minimum API version is 1.44).
5. Record each node's environment: `ssh ubuntu@NODE 'bash -s' < envspec.sh > NODE.txt`.
6. Table I / party grid: `run_smpc_aws.sh N K` for n in {4, 8, 12, 16}, k in {10 000, 50 000}.
7. Table II: `aws_fabric.sh F1`, `F1R`, then `orchestrate_node2.sh` (64 client workers) and
   `orchestrate_node3.sh` (3-org configurations) on the Fabric node.
8. Table III / Table V: `run_pipeline_aws.sh N K [T]` from the control host or, as used for most
   configurations, `orchestrate_node.sh` on the Fabric node, which calls `node_run_pipeline.sh`.
9. Copy the outputs back and run `cleanup.sh` (tag-scoped teardown).

`nodes.txt` (control host) has one tab-separated line per SMPC node: index, instance id, public IP,
private IP, AZ, placement group. `nodes_private.txt` (Fabric node) has index and private IP.

| Script | Role |
|---|---|
| `userdata.sh` | Failsafe: shuts the instance down (and so terminates it) after 5 hours |
| `setup_node.sh` | Software install on the image node |
| `envspec.sh` | Per-node environment record |
| `pssh.sh` | Runs one command on all SMPC nodes (used for the RTT matrix) |
| `run_smpc_aws.sh` | Multi-host online SMPC benchmark (`layer-2/smpc_bench.py`) |
| `run_pipeline_aws.sh`, `node_run_pipeline.sh` | Multi-host pipeline benchmark (`harness/pipeline_bench.py`) |
| `aws_fabric.sh` | Fabric configuration and load phases (`harness/fabric_config.sh`, `harness/fabric_bench.py`) |
| `orchestrate_node.sh`, `orchestrate_node2.sh`, `orchestrate_node3.sh` | On-node sequences for the pipeline grid and the Fabric grid |
| `cleanup.sh` | Deletes every resource carrying the project tag |

Output folders written by these scripts (`results/smpc_online/aws/...`, `results/pipeline/aws/...`,
`run/out/fabric/...`) correspond to `smpc_online/`, `pipeline/` and `fabric/` in
`results/aws_2026-11-12/`.

## fabric-samples changes

[`../fabric-samples-local.diff`](../fabric-samples-local.diff) is the difference between the
fabric-samples working copy that was copied to the nodes and fabric-samples commit 7f0f4a2: it sets
`CORE_CHAINCODE_BUILDER=hyperledger/fabric-ccenv:2.5.12` for the test-network peers (Org1, Org2 and
Org3). Peer, orderer and the other Fabric images were 2.5.4 (`setup_node.sh`); the node image list
recorded in `results/aws_2026-11-12/logs/run/out/docker_images.txt` contains `fabric-ccenv:2.5.4` only.
Apply the diff with `git -C layer-3/fabric-samples apply ../../deploy/fabric-samples-local.diff`.
