#!/bin/bash

sudo yum groupinstall "development tools"
sudo yum install bzip2-devel gdbm-devel libffi-devel \
  libuuid-devel ncurses-devel openssl-devel readline-devel \
  sqlite-devel tk-devel wget xz-devel zlib-devel
