from .Entity import Entity
from .NeuralNetwork import NeuralNetwork
class Prey(Entity):
    def init(self,dna, x, y, radius):
        super(x, y, radius)
        self.type=2
        self.health=100
        self.energy=100
        self.age=0
        self.score=0
        self.brain=NeuralNetwork(dna)