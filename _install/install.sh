#!/bin/bash


# install PNGView
wget -P ~ https://github.com/AndrewFromMelbourne/raspidmx/archive/master.zip
unzip ~/master.zip -d ~

make --directory=~/raspidmx-master

sudo mv ~/raspidmx-master/pngview/pngview /usr/bin
sudo chown root:root /usr/bin/pngview
sudo chmod 755 /usr/bin/pngview

rm ~/master.zip
sudo rm -r ~/raspidmx-master


# install RClone
wget -P ~ https://downloads.rclone.org/rclone-current-linux-arm.zip
unzip ~/rclone-current-linux-arm.zip -d ~

cd ~/rclone-v*
sudo mv rclone /usr/bin
sudo chown root:root /usr/bin/rclone
sudo chmod 755 /usr/bin/rclone

cd ~
rm ~/rclone-current-linux-arm.zip
rm -r ~/rclone-v*


# install ImageMagick
sudo apt-get update
sudo apt-get --yes install imagemagick