# =====================================================================================================
# setup_node.sh — MDCOLAB-CHAIN AWS run (12 Nov 2026): one-time software install on the builder node
# (c6i.2xlarge, Ubuntu 24.04 LTS AMI from Canonical), after which an AMI was created from that node and
# all 16 SMPC nodes were launched from the AMI (so every node has identical software).
# Installs: python3.12-venv, Docker, jq, ping, iperf3; venv /home/ubuntu/venv with mpyc==0.9, numpy<2, psutil
# (repo requirements.txt); pulls Hyperledger Fabric 2.5.4 images (peer, orderer, ccenv, baseos) and fabric-ca 1.5.17.
# Input: /home/ubuntu/payload.tgz = repo copy MDCOLAB-CHAIN (fix/runnable 03f1599, no venv/results/certs) + harness/.
# Feeds: all AWS tables (environment only). Rerun: scp payload.tgz + this file to a fresh node; bash setup_node.sh.
# Later fixes on the Fabric node only (see results/aws_2026-11-12/README.md): apt golang-go (chaincode vendoring needs go),
# and Docker Engine replaced by docker-ce 28.5.2 + compose plugin, because Ubuntu's docker.io 29.1.3 rejects the
# Docker API version used by Fabric 2.5.4's chaincode builder (min API 1.44) -> chaincode install failed.
# =====================================================================================================
set -e
export DEBIAN_FRONTEND=noninteractive
sudo apt-get update -qq
sudo apt-get install -y -qq python3.12-venv python3-pip docker.io jq iputils-ping iperf3 sysstat >/dev/null
sudo usermod -aG docker ubuntu
cd /home/ubuntu && tar xzf payload.tgz && rm payload.tgz
python3.12 -m venv /home/ubuntu/venv
/home/ubuntu/venv/bin/pip install -q mpyc==0.9 'numpy<2' psutil
for i in peer:2.5.4 orderer:2.5.4 ccenv:2.5.4 baseos:2.5.4; do sudo docker pull -q hyperledger/fabric-$i; done
sudo docker pull -q hyperledger/fabric-ca:1.5.17
for i in peer orderer ccenv baseos; do sudo docker tag hyperledger/fabric-$i:2.5.4 hyperledger/fabric-$i:latest; sudo docker tag hyperledger/fabric-$i:2.5.4 hyperledger/fabric-$i:2.5; done
sudo docker tag hyperledger/fabric-ca:1.5.17 hyperledger/fabric-ca:latest
/home/ubuntu/venv/bin/pip freeze
echo SETUP_DONE
