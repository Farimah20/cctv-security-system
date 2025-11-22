#!/bin/bash

# Fix Wayland display issue
export QT_QPA_PLATFORM=xcb
export DISPLAY=:0

# Activate conda environment
source ~/anaconda3/etc/profile.d/conda.sh
conda activate cctv_monitor

# Run surveillance test
python test_detection.py

