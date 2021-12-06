#!/usr/bin/bash
set -ex
sudo apt install git flake8 -y

git clone "https://${mpr_url}/black-bin"
cd black-bin/
makedeb -si --no-confirm
cd ../
rm black-bin/ -rf

flake8 ./
black --check ./
