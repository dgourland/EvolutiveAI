"""
dna.py

Gestion de l'ADN des créatures.

L'ADN est une liste de nombres flottants.

Chaque valeur représente un gène.
Dans notre simulation, les gènes correspondent
principalement aux poids du réseau neuronal.
"""
import base64

import numpy as np
import random



class DNA:


    def __init__(
        self,
        genes
    ):

        self.genes = np.array(
            genes,
            dtype=np.float32
        )



    # -----------------------------------------------------
    # Création aléatoire
    # -----------------------------------------------------

    @classmethod
    def random(
        cls,
        size
    ):

        """

        Crée un ADN aléatoire.

        Exemple :

        DNA.random(1456)

        """

        genes = np.random.uniform(
            -1,
            1,
            size
        )


        return cls(
            genes
        )



    # -----------------------------------------------------
    # Copie
    # -----------------------------------------------------

    def copy(self):

        return DNA(
            self.genes.copy()
        )



    # -----------------------------------------------------
    # Mutation
    # -----------------------------------------------------

    def mutate(
        self,
        rate=0.02,
        strength=0.2
    ):

        """
        Mutation aléatoire.

        rate :
            probabilité qu'un gène mute.

        strength :
            intensité de la mutation.
        """


        child = self.genes.copy()



        for i in range(
            len(child)
        ):


            if random.random() < rate:


                child[i] += np.random.normal(
                    0,
                    strength
                )



        return DNA(
            child
        )
    
    def dumpDna(self):
        return base64.b64encode(self.genes.tobytes()).decode("utf-8")

    def loadDna(self, dna_dump:str):
        self.genes = np.frombuffer(
            base64.b64decode(dna_dump.encode("utf-8"))
            , dtype=np.float32
        )



    # -----------------------------------------------------
    # Croisement
    # -----------------------------------------------------

    def crossover(
        self,
        other
    ):

        """
        Mélange deux ADN.

        Exemple :

        Parent A
        111111

        Parent B
        000000


        Enfant :

        110010
        """



        if len(self.genes) != len(other.genes):

            raise ValueError(
                "ADN incompatibles"
            )


        child = np.empty_like(
            self.genes
        )


        for i in range(
            len(child)
        ):


            if random.random() < 0.5:

                child[i] = self.genes[i]

            else:

                child[i] = other.genes[i]



        return DNA(
            child
        )



    # -----------------------------------------------------
    # Accès
    # -----------------------------------------------------

    def __len__(self):

        return len(
            self.genes
        )



    def __getitem__(
        self,
        index
    ):

        return self.genes[index]



    def __repr__(self):

        return (
            f"DNA(size={len(self.genes)})"
        )