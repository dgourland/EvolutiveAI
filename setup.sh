sudo apt -y install python3.13-venv
python3 -m venv .
./bin/pip install numpy pygame-ce pygame
mkdir -p saves/preys
mkdir -p saves/predator
mkdir logs