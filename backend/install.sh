#!/bin/bash
apt update

apt install python3-pip -y
mv /usr/lib/python3.12/EXTERNALLY-MANAGED{,.bak}
pip config set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple

pip3 install -r requirements.txt

apt install rabbitmq-server -y

# install ipfs
wget --no-check-certificate https://dist.ipfs.tech/kubo/v0.31.0/kubo_v0.31.0_linux-amd64.tar.gz
tar -zxf kubo_v0.31.0_linux-amd64.tar.gz
cp kubo/ipfs /usr/local/bin/

sed -i "/IPFS_PATH/d" /etc/profile
echo "export IPFS_PATH=/data/ipfsrepo" >> /etc/profile
source /etc/profile

cp ipfs.service /lib/systemd/system/ipfs.service

ipfs init
ipfs config --json API.HTTPHeaders.Access-Control-Allow-Origin "[\"*\"]"
ipfs config --json API.HTTPHeaders.Access-Control-Allow-Credentials "[\"true\"]"
ipfs config --json API.HTTPHeaders.Access-Control-Allow-Methods "[\"PUT\", \"POST\", \"GET\"]"
ipfs config Datastore.StorageMax 10GB
ipfs config --json Experimental.FilestoreEnabled true

systemctl enable ipfs.service
systemctl start ipfs.service