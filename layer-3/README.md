# Layer 3 (Hyperledger Fabric)

Clone `fabric-samples` into this directory and install the Fabric binaries:

```bash
git clone https://github.com/hyperledger/fabric-samples.git layer-3/fabric-samples
git -C layer-3/fabric-samples checkout 7f0f4a24fad0f27c952a7d8381d6f7fb4b737871
cd layer-3/fabric-samples
curl -sSLO https://raw.githubusercontent.com/hyperledger/fabric/main/scripts/install-fabric.sh
chmod +x install-fabric.sh
./install-fabric.sh --fabric-version 2.5.4 docker binary
```

Start the network and deploy the `basic` chaincode:

```bash
cd test-network
./network.sh up createChannel -c mychannel
./network.sh deployCC -ccn basic -ccp ../asset-transfer-basic/chaincode-go -ccl go
```

`automate_layers.py` runs `test-network/blockchain.py` in this working copy. See the top-level README §5.
