from Prey import Prey
import numpy as np
DNA_SIZE = 20
dna=dna = np.random.uniform(-1,1,DNA_SIZE)
x=10
y=10
radius=20
prey =Prey(dna, x, y, radius)
print(prey.health)
print(prey.energy)