#!/bin/bash

wget -P ~ https://github.com/AndrewFromMelbourne/raspidmx/archive/master.zip
unzip ~/master.zip -d ~

make --directory=~/raspidmx-master

sudo mv ~/raspidmx-master/pngview/pngview /usr/bin
#sudo mv ~/raspidmx-master/lib/libraspidmx.so.1 /usr/lib
sudo chown root:root /usr/bin/pngview
sudo chmod 755 /usr/bin/pngview

rm ~/master.zip
sudo rm -r ~/raspidmx-master