#!/usr/bin/env bash
# BUILDER Launcher script
APP_DIR="/home/kevin/BUILDER"
export PYTHONPATH="$APP_DIR:$PYTHONPATH"
python3 "$APP_DIR/builder.py" "$@"
