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
if [ ! -d ${IPFS_PATH} ];then
    mkdir -p ${IPFS_PATH}
fi

cp ipfs.service /lib/systemd/system/ipfs.service

ipfs init
ipfs config --json API.HTTPHeaders.Access-Control-Allow-Origin "[\"*\"]"
ipfs config --json API.HTTPHeaders.Access-Control-Allow-Credentials "[\"true\"]"
ipfs config --json API.HTTPHeaders.Access-Control-Allow-Methods "[\"PUT\", \"POST\", \"GET\"]"
ipfs config Datastore.StorageMax 10GB
ipfs config --json Experimental.FilestoreEnabled true

systemctl enable ipfs.service
systemctl start ipfs.service

apt install ffmpeg -y
apt install jq -y
storage=$(cat config.json | jq -r 'to_entries|.[]| select(.key == "local-storage")|.value')
if [ ! -d ${storage} ];then
    mkdir -p ${storage}
fi

# install app
mkdir /opt/vs-upload-helper
cp *.py /opt/vs-upload-helper/
cp config.json /opt/vs-upload-helper/
cp vs-upload-helper.service /lib/systemd/system/vs-upload-helper.service
cp vs-upload-runner.service /etc/systemd/system/vs-upload-runner.service
systemctl enable vs-upload-helper.service
systemctl start vs-upload-helper.service
systemctl enable vs-upload-runner.service
systemctl start vs-upload-runner.service


apt install -y nginx-full
cp vs-upload-helper.conf /etc/nginx/sites-enabled/default
