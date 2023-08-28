#!/bin/sh
echo setting dekryption key for testing
export KREATE_KRYPT_KEY_DEV=C6XOvZALFPjTzWKOPV3EJFIpmmwMhXEE


echo '###########################################'
echo python3 -m kreate.kube --konf tests/demo/konfig.yaml -w test
python3 -m kreate.kube --konf tests/demo/konfig.yaml -w test

echo '###########################################'
echo ./tests/demo/kreate-demo-from-script.py --konf ./tests/demo -w test
./tests/demo/kreate-demo-from-script.py --konf ./tests/demo -w test

echo '###########################################'
echo ./tests/demo/kreate-demo-from-strukt.py --konf ./tests/demo -w test
./tests/demo/kreate-demo-from-strukt.py --konf ./tests/demo  -w test
