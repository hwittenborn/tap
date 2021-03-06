#!/usr/bin/bash
set -ex
sudo -E apt-get install git flake8 -y

git clone "https://${mpr_url}/black-bin"
cd black-bin/
makedeb -s --no-confirm
sudo -E apt-get install ./black-bin*.deb -y

cd ../
rm black-bin/ -rf

flake8 ./
black --check ./
