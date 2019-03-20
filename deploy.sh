#!/bin/bash

eval "$(ssh-agent -s)" &&
ssh-add -k ~/.ssh/id_rsa &&
cd /home/ubuntu/travis_API_dari_testdocker2
git pull

source ~/.profile
echo "$DOCKERHUB_PASS" | sudo docker login --username $DOCKERHUB_USER --password-stdin
sudo docker stop hello4
sudo docker rm hello4
sudo docker rmi blasterb0y/helloworld
sudo docker run -d --name hello4 -p 5000:5000 blasterb0y/helloworld:latest
