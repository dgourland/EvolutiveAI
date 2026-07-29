"""
App/genetics/dna.py

Gestion de l'ADN des créatures.

L'ADN est un simple vecteur de nombres flottants.

Il peut être :

- généré aléatoirement
- copié
- muté
- croisé
- exporté/importé

Le contenu des gènes est interprété
par les différents systèmes (cerveau,
corps, capteurs, etc.).
"""

import base64
import random

import numpy as np


class DNA:

    def __init__(self, genes):

        self.genes = np.asarray(
            genes,
            dtype=np.float32
        )

    # =====================================================
    # Création
    # =====================================================

    @classmethod
    def random(cls, size):

        return cls(

            np.random.uniform(
                -1.0,
                1.0,
                size
            )

        )

    # =====================================================
    # Copie
    # =====================================================

    def copy(self):

        return DNA(
            self.genes.copy()
        )

    # =====================================================
    # Mutation
    # =====================================================

    def mutate(
        self,
        rate=0.02,
        strength=0.20
    ):
        """
        Mutation gaussienne.

        Chaque gène possède une probabilité
        'rate' d'être modifié.

        La variation suit une loi normale.
        """

        child = self.genes.copy()

        mask = np.random.random(
            len(child)
        ) < rate

        child[mask] += np.random.normal(
            0,
            strength,
            np.count_nonzero(mask)
        )

        return DNA(child)

    # =====================================================
    # Croisement
    # =====================================================

    def crossover(self, other):

        if len(self) != len(other):

            raise ValueError(
                "Les ADN n'ont pas la même taille."
            )

        mask = np.random.random(
            len(self)
        ) < 0.5

        child = np.where(
            mask,
            self.genes,
            other.genes
        )

        return DNA(child)

    # =====================================================
    # Encodage
    # =====================================================

    def dump(self):

        return base64.b64encode(
            self.genes.tobytes()
        ).decode("utf-8")

    @classmethod
    def load(cls, dump):

        genes = np.frombuffer(
            base64.b64decode(
                dump.encode("utf-8")
            ),
            dtype=np.float32
        )

        return cls(genes)

    # =====================================================
    # Accès
    # =====================================================

    def __len__(self):

        return len(self.genes)

    def __getitem__(self, index):

        return self.genes[index]

    def __setitem__(self, index, value):

        self.genes[index] = value

    def __iter__(self):

        return iter(self.genes)

    # =====================================================
    # Affichage
    # =====================================================

    def __repr__(self):

        return (
            f"DNA(size={len(self)})"
        )