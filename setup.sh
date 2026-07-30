sudo apt -y install python3.13-venv
python3 -m venv .
./bin/pip install numba pygame-ce pygame
mkdir -p saves/preys
mkdir -p saves/predator
mkdir logs