#!/bin/bash

wget https://github.com/xonsh/xonsh/releases/latest/download/xonsh-x86_64.AppImage
chmod +x xonsh-x86_64.AppImage
sudo mv xonsh-x86_64.AppImage /bin/xonsh
sudo chmod 777 /bin/xonsh
