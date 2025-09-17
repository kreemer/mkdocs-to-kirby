#!/bin/bash
set -e
sudo apt-get install -y bats
pip install -e .

bats tests/
