#!/bin/sh

termine_src=$(builtin cd $(dirname $0)/..; pwd)
export PYTHONPATH=$termine_src/Shell:$termine_src/TUI

./Main.py
