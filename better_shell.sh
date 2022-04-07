#!/bin/bash

touch /bin/sim
sudo chmod 777 /bin/sim

echo "python3 -m suplemon" >> /bin/sim
python3 -m pip install --upgrade suplemon
sim
