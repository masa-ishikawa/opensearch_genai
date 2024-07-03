#!/bin/bash

cd ~
wget https://www.python.org/ftp/python/3.12.4/Python-3.12.4.tar.xz
tar xJf Python-3.12.4.tar.xz
cd Python-3.12.4
./configure
make
sudo make install
sudo ln -sf $(which python3.12) /usr/bin/python
sudo ln -sf $(which pip3.12) /usr/bin/pip