#!/bin/bash

apt-get install wget -y

wget https://github.com/xonsh/xonsh/releases/latest/download/xonsh-x86_64.AppImage
chmod +x xonsh-x86_64.AppImage
mv xonsh-x86_64.AppImage /bin/xonsh
chmod 777 /bin/xonsh
/bin/xonsh
