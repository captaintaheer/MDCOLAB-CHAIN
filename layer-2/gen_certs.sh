#!/usr/bin/env bash
# Generate a throw-away CA and per-party TLS certificates for MPyC's --ssl option.
# MPyC 0.9 (runtime.py:211-213) expects .config/party_<pid>.crt/.key and .config/mpyc_ca.crt in the
# working directory, and verifies the peer name 'MPyC party <pid>' (runtime.py:238).
# Usage: ./gen_certs.sh <max_parties>   (keys are git-ignored; never commit them)
set -euo pipefail
M=${1:-16}
cd "$(dirname "$0")"; mkdir -p .config; cd .config
openssl req -x509 -newkey rsa:2048 -nodes -days 30 -subj "/CN=MPyC CA" -keyout mpyc_ca.key -out mpyc_ca.crt 2>/dev/null
for ((i=0;i<M;i++)); do
  openssl req -newkey rsa:2048 -nodes -subj "/CN=MPyC party $i" -keyout party_$i.key -out party_$i.csr 2>/dev/null
  openssl x509 -req -in party_$i.csr -CA mpyc_ca.crt -CAkey mpyc_ca.key -CAcreateserial -days 30 -out party_$i.crt 2>/dev/null
  rm party_$i.csr
done
echo "generated certificates for $M parties in $(pwd)"
