#!/bin/sh
python processing.py
python processing.py 1
python processing.py 10
python processing.py 100
python processing.py None 1000
python processing.py None 900
python processing.py None 800
python processing.py 1 1000
python processing.py 10 900
python processing.py 100 800

python3 evaluation.py
