#!/bin/bash

sudo apt-get update -y
#sudo apt-get install wget -y

#wget https://github.com/xonsh/xonsh/releases/latest/download/xonsh-x86_64.AppImage
#chmod +x xonsh-x86_64.AppImage
#sudo mv xonsh-x86_64.AppImage /bin/xonsh
#sudo chmod 777 /bin/xonsh
#/bin/xonsh

touch /bin/xonsh
sudo chmod 777 /bin/xonsh

echo "python3 -m xonsh" >> /bin/xonsh
python3 -m pip install --upgrade xonsh
xonsh
