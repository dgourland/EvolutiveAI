"""
App/brain/neural_network.py

Réseau neuronal évolutif.

Le réseau ne possède aucun apprentissage.
Tous les paramètres viennent de l'ADN.

Le réseau possède une mémoire interne :
- il reçoit une mémoire précédente ;
- il produit une nouvelle mémoire.
"""


import numpy as np



class NeuralNetwork:


    def __init__(
        self,
        dna,
        input_size,
        memory_size=16,
        hidden1_size=32,
        hidden2_size=32,
        output_size=5
    ):

        self.input_size = input_size

        self.memory_size = memory_size

        self.hidden1_size = hidden1_size

        self.hidden2_size = hidden2_size

        self.output_size = output_size


        self.total_input_size = (
            input_size
            + memory_size
        )


        self.load_dna(
            dna
        )


    # =====================================================
    # Chargement ADN
    # =====================================================

    def load_dna(self, dna):

        index = 0


        # -------------------------------------------------
        # Couche 1
        # -------------------------------------------------

        size = (
            self.total_input_size
            *
            self.hidden1_size
        )

        self.w1 = np.array(
            dna[index:index+size],
            dtype=np.float32
        ).reshape(
            self.total_input_size,
            self.hidden1_size
        )

        index += size


        self.b1 = np.array(
            dna[index:index+self.hidden1_size],
            dtype=np.float32
        )

        index += self.hidden1_size


        # -------------------------------------------------
        # Couche 2
        # -------------------------------------------------

        size = (
            self.hidden1_size
            *
            self.hidden2_size
        )


        self.w2 = np.array(
            dna[index:index+size],
            dtype=np.float32
        ).reshape(
            self.hidden1_size,
            self.hidden2_size
        )


        index += size


        self.b2 = np.array(
            dna[index:index+self.hidden2_size],
            dtype=np.float32
        )


        index += self.hidden2_size



        # -------------------------------------------------
        # Sortie actions
        # -------------------------------------------------

        size = (
            self.hidden2_size
            *
            self.output_size
        )


        self.w_action = np.array(
            dna[index:index+size],
            dtype=np.float32
        ).reshape(
            self.hidden2_size,
            self.output_size
        )


        index += size


        self.b_action = np.array(
            dna[index:index+self.output_size],
            dtype=np.float32
        )


        index += self.output_size



        # -------------------------------------------------
        # Sortie mémoire
        # -------------------------------------------------

        size = (
            self.hidden2_size
            *
            self.memory_size
        )


        self.w_memory = np.array(
            dna[index:index+size],
            dtype=np.float32
        ).reshape(
            self.hidden2_size,
            self.memory_size
        )


        index += size


        self.b_memory = np.array(
            dna[index:index+self.memory_size],
            dtype=np.float32
        )



    # =====================================================
    # Propagation
    # =====================================================

    def forward(
        self,
        inputs,
        memory
    ):

        """
        Retourne :

        actions
        nouvelle mémoire
        """


        # -------------------------------------------------
        # Fusion perception + mémoire
        # -------------------------------------------------

        neural_input = np.concatenate(
            (
                inputs,
                memory
            )
        )


        # -------------------------------------------------
        # Couche cachée 1
        # -------------------------------------------------

        hidden1 = np.tanh(
            neural_input @ self.w1
            +
            self.b1
        )


        # -------------------------------------------------
        # Couche cachée 2
        # -------------------------------------------------

        hidden2 = np.tanh(
            hidden1 @ self.w2
            +
            self.b2
        )


        # -------------------------------------------------
        # Actions
        # -------------------------------------------------

        actions = np.tanh(
            hidden2 @ self.w_action
            +
            self.b_action
        )


        # -------------------------------------------------
        # Nouvelle mémoire
        # -------------------------------------------------

        new_memory = np.tanh(
            hidden2 @ self.w_memory
            +
            self.b_memory
        )


        return (
            actions,
            new_memory
        )



    # =====================================================
    # Taille ADN nécessaire
    # =====================================================

    @staticmethod
    def dna_size(
        input_size,
        memory_size=16,
        hidden1_size=32,
        hidden2_size=32,
        output_size=5
    ):


        total_input = (
            input_size
            +
            memory_size
        )


        return (

            # couche 1
            total_input
            *
            hidden1_size

            +
            hidden1_size


            # couche 2
            +
            hidden1_size
            *
            hidden2_size

            +
            hidden2_size


            # actions
            +
            hidden2_size
            *
            output_size

            +
            output_size


            # mémoire
            +
            hidden2_size
            *
            memory_size

            +
            memory_size
        )