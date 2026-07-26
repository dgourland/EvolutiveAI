"""
neural_network.py

Réseau neuronal utilisé par les créatures.

Les poids sont fournis par l'ADN.
Aucun apprentissage classique.

L'évolution modifie directement les poids.
"""


import numpy as np



class NeuralNetwork:


    def __init__(
        self,
        dna,
        input_size,
        hidden1_size=32,
        hidden2_size=16,
        output_size=5
    ):


        self.input_size = input_size

        self.hidden1_size = hidden1_size

        self.hidden2_size = hidden2_size

        self.output_size = output_size



        self.load_dna(
            dna
        )

    def forward_batch(
        self,
        inputs
    ):
        

        layer1 = np.tanh(
            inputs @ self.w1 + self.b1
        )

        layer2 = np.tanh(
            layer1 @ self.w2 + self.b2
        )

        output = np.tanh(
            layer2 @ self.w3 + self.b3
        )

        return output

    # -----------------------------------------------------
    # Construction depuis ADN
    # -----------------------------------------------------

    def load_dna(self, dna):

        index = 0

        # ---------------- W1 ----------------

        size_w1 = self.input_size * self.hidden1_size

        self.w1 = np.array(
            dna[index:index + size_w1],
            dtype=np.float32
        ).reshape(
            self.input_size,
            self.hidden1_size
        )

        index += size_w1

        # ---------------- b1 ----------------

        self.b1 = np.array(
            dna[index:index + self.hidden1_size],
            dtype=np.float32
        )

        index += self.hidden1_size

        # ---------------- W2 ----------------

        size_w2 = self.hidden1_size * self.hidden2_size

        self.w2 = np.array(
            dna[index:index + size_w2],
            dtype=np.float32
        ).reshape(
            self.hidden1_size,
            self.hidden2_size
        )

        index += size_w2

        # ---------------- b2 ----------------

        self.b2 = np.array(
            dna[index:index + self.hidden2_size],
            dtype=np.float32
        )

        index += self.hidden2_size

        # ---------------- W3 ----------------

        size_w3 = self.hidden2_size * self.output_size

        self.w3 = np.array(
            dna[index:index + size_w3],
            dtype=np.float32
        ).reshape(
            self.hidden2_size,
            self.output_size
        )

        index += size_w3

        # ---------------- b3 ----------------

        self.b3 = np.array(
            dna[index:index + self.output_size],
            dtype=np.float32
        )



    # -----------------------------------------------------
    # Calcul neuronal
    # -----------------------------------------------------

    def forward(
        self,
        inputs
    ):

        layer1 = np.tanh(
            np.dot(inputs, self.w1) + self.b1
        )

        layer2 = np.tanh(
            np.dot(layer1, self.w2) + self.b2
        )

        output = np.tanh(
            np.dot(layer2, self.w3) + self.b3
        )

        return output



    # -----------------------------------------------------
    # Nombre de gènes nécessaires
    # -----------------------------------------------------

    @staticmethod
    @staticmethod
    def dna_size(
        input_size,
        hidden1_size=32,
        hidden2_size=16,
        output_size=5
    ):

        return (

            input_size * hidden1_size
            + hidden1_size          # b1

            + hidden1_size * hidden2_size
            + hidden2_size          # b2

            + hidden2_size * output_size
            + output_size           # b3
        )