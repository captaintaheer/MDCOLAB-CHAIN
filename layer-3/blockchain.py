#!/usr/bin/env python3
"""Layer 3 readiness check for the Hyperledger Fabric test-network.

automate_layers.py runs this file as its Layer 3 step when the fabric-samples working copy has no
test-network/blockchain.py. It checks that the 'basic' chaincode is committed on 'mychannel'
(peer lifecycle chaincode querycommitted) and exits 0 if so, 1 otherwise. The ledger transactions
and their timing are done by automate_layers.collect_ledger_metrics().

FABRIC_TEST_NETWORK selects the test-network directory
(default: layer-3/fabric-samples/test-network next to this file).
"""
import os, subprocess, sys
here = os.path.dirname(os.path.abspath(__file__))
tn = os.environ.get('FABRIC_TEST_NETWORK', os.path.join(here, 'fabric-samples', 'test-network'))
org1 = os.path.join(tn, 'organizations/peerOrganizations/org1.example.com')
env = dict(os.environ, FABRIC_CFG_PATH=os.path.join(tn, '..', 'config'), CORE_PEER_TLS_ENABLED='true',
           CORE_PEER_LOCALMSPID='Org1MSP', CORE_PEER_ADDRESS='localhost:7051',
           CORE_PEER_TLS_ROOTCERT_FILE=os.path.join(org1, 'peers/peer0.org1.example.com/tls/ca.crt'),
           CORE_PEER_MSPCONFIGPATH=os.path.join(org1, 'users/Admin@org1.example.com/msp'))
peer = os.path.join(tn, '..', 'bin', 'peer')
try:
    p = subprocess.run([peer, 'lifecycle', 'chaincode', 'querycommitted', '-C', 'mychannel', '-n', 'basic'],
                       env=env, capture_output=True, text=True)
except OSError as e:
    print(f'peer CLI not available: {e}')
    sys.exit(1)
print(p.stdout.strip() or p.stderr.strip())
print('basic chaincode committed on mychannel' if p.returncode == 0 else 'basic chaincode not available on mychannel')
sys.exit(p.returncode)
