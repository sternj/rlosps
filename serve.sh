#!/bin/bash

python3 render.py
cp -R images docs
cd docs
python3 -m http.server