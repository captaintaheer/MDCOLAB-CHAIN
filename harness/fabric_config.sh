#!/usr/bin/env bash
# (Re)create the Fabric 2.5.4 test-network with a given orderer batch configuration, org count and
# chaincode endorsement policy, then deploy asset-transfer-basic (Go).
# Usage: fabric_config.sh BATCH_TIMEOUT MAX_MESSAGE_COUNT ORGS(2|3) POLICY(majority|any) SNAPSHOT_DIR
set -euo pipefail
BT=$1; MMC=$2; ORGS=$3; POL=$4; SNAP=$5
H=${HARNESS_DIR:-$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)}
TN=${FABRIC_TEST_NETWORK:-$H/../layer-3/fabric-samples/test-network}
mkdir -p $SNAP
cd $TN
export PATH=$TN/../bin:$PATH FABRIC_CFG_PATH=$TN/../config
./network.sh down > $SNAP/network_down.log 2>&1 || true
docker rm -f $(docker ps -aq) >/dev/null 2>&1 || true
echo 0 | sudo tee /proc/sys/net/bridge/bridge-nf-call-iptables >/dev/null || true
cp $H/configtx.stock.yaml configtx/configtx.yaml
sed -i "s/^  BatchTimeout: 2s/  BatchTimeout: ${BT}/; s/^    MaxMessageCount: 10/    MaxMessageCount: ${MMC}/" configtx/configtx.yaml
diff $H/configtx.stock.yaml configtx/configtx.yaml > $SNAP/configtx.diff || true
./network.sh up createChannel -c mychannel > $SNAP/network_up.log 2>&1
if [ "$ORGS" = 3 ]; then (cd addOrg3 && ./addOrg3.sh up -c mychannel > $SNAP/addOrg3.log 2>&1); fi
EP=""
if [ "$POL" = any ]; then
  if [ "$ORGS" = 3 ]; then EP="OR('Org1MSP.peer','Org2MSP.peer','Org3MSP.peer')"; else EP="OR('Org1MSP.peer','Org2MSP.peer')"; fi
  ./network.sh deployCC -ccn basic -ccp ../asset-transfer-basic/chaincode-go -ccl go -ccep "$EP" > $SNAP/deployCC.log 2>&1
else
  ./network.sh deployCC -ccn basic -ccp ../asset-transfer-basic/chaincode-go -ccl go > $SNAP/deployCC.log 2>&1
fi
if [ "$ORGS" = 3 ]; then
  ( set +euo pipefail; . scripts/envVar.sh; . scripts/ccutils.sh; . scripts/utils.sh
    CHANNEL_NAME=mychannel CC_NAME=basic CC_VERSION=1.0 CC_SEQUENCE=1 INIT_REQUIRED="" CC_COLL_CONFIG=""
    if [ -n "$EP" ]; then CC_END_POLICY="--signature-policy $EP"; else CC_END_POLICY=""; fi
    PACKAGE_ID=$(peer lifecycle chaincode calculatepackageid basic.tar.gz)
    installChaincode 3; approveForMyOrg 3 ) > $SNAP/org3_install_approve.log 2>&1
fi
# snapshot of the effective channel config
set +u; . scripts/envVar.sh; setGlobals 1
peer channel fetch config $SNAP/config_block.pb -o localhost:7050 --ordererTLSHostnameOverride orderer.example.com -c mychannel --tls --cafile "$ORDERER_CA" > /dev/null 2>&1
configtxlator proto_decode --input $SNAP/config_block.pb --type common.Block | jq '.data.data[0].payload.data.config | {batch_timeout: .channel_group.groups.Orderer.values.BatchTimeout.value, batch_size: .channel_group.groups.Orderer.values.BatchSize.value, orgs: (.channel_group.groups.Application.groups|keys), app_endorsement: .channel_group.groups.Application.policies.Endorsement.policy}' > $SNAP/effective_channel_config.json
rm -f $SNAP/config_block.pb
peer lifecycle chaincode querycommitted -C mychannel -n basic --output json > $SNAP/chaincode_definition.json 2>/dev/null || true
docker ps --format '{{.Names}} {{.Image}}' > $SNAP/containers.txt
cat $SNAP/effective_channel_config.json
