import numpy as np

class NeuralNetwork:

    def __init__(self, dna):

        self.w1 = dna[:12].reshape((3,4))
        self.w2 = dna[12:].reshape((4,2))

    def forward(self, inputs):

        hidden = np.tanh(np.dot(inputs, self.w1))
        output = np.tanh(np.dot(hidden, self.w2))

        return output