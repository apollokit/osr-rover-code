#!/bin/bash
set -e

SCRIPT_DIR=$(dirname $(realpath $0))

source $SCRIPT_DIR/source_virtualenv

OSR_SRC_DIR=$(realpath $SCRIPT_DIR/../../ROS/osr/src)

PYTHONPATH=$PYTHONPATH:$OSR_SRC_DIR "$@"
