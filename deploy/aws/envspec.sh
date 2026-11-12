# =====================================================================================================
# envspec.sh — MDCOLAB-CHAIN AWS run (12 Nov 2026): per-node environment record (results/aws_2026-11-12/env/*.txt).
# Prints instance type, AMI, AZ/AZ-id, placement group, private IP (from IMDSv2), nproc, free -m, lscpu,
# OS release, kernel, Python and pip freeze of the benchmark venv, Docker version.
# Feeds:  rows "EC2 instance type, vCPU, RAM", "OS image, region, placement", "MPyC version"; Section IV-B.
# Rerun: ssh ubuntu@NODE 'bash -s' < envspec.sh > env_NODE.txt   (public and private IPs and resource IDs are redacted in the repository copy)
# =====================================================================================================
T=$(curl -s -X PUT http://169.254.169.254/latest/api/token -H 'X-aws-ec2-metadata-token-ttl-seconds: 300')
md() { curl -s -H "X-aws-ec2-metadata-token: $T" http://169.254.169.254/latest/meta-data/$1; }
echo "instance_id: $(md instance-id)"; echo "instance_type: $(md instance-type)"; echo "ami_id: $(md ami-id)"
echo "az: $(md placement/availability-zone)"; echo "az_id: $(md placement/availability-zone-id)"; echo "placement_group: $(md placement/group-name)"; echo "private_ip: $(md local-ipv4)"
echo "nproc: $(nproc)"; free -m | sed 's/^/free: /'; lscpu | sed 's/^/lscpu: /'
. /etc/os-release; echo "os: $PRETTY_NAME"; echo "kernel: $(uname -r)"
echo "python: $(/home/ubuntu/venv/bin/python -V 2>&1)"; /home/ubuntu/venv/bin/pip freeze | sed 's/^/pip: /'
docker --version 2>/dev/null | sed 's/^/docker: /'
