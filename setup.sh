sudo apt -y install python3.13-venv
python3 -m venv .
./bin/pip install numba pygame-ce pygame scipy PyOpenGL PyOpenGL_accelerate 
mkdir -p saves/default/preys
mkdir -p saves/default/predator
mkdir logs