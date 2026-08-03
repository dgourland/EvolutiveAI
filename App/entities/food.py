"""
App/entities/food.py

Entité nourriture.

Une nourriture possède :

- une position
- une taille
- une énergie donnée à une créature

Elle est utilisée par :
    - SpatialGrid
    - Raycaster
    - World
"""


import random
from App.vars import FOOD



class Food:


    def __init__(
        self,
        x=None,
        y=None,
        world_width=None,
        world_height=None
    ):


        # ------------------------------------------------
        # Position
        # ------------------------------------------------
        self.last_ray_query=-1
        self.energy=40
        if x is not None and y is not None:

            self.x = x
            self.y = y

        else:

            self.x = random.uniform(
                0,
                world_width
            )

            self.y = random.uniform(
                0,
                world_height
            )


        # ------------------------------------------------
        # Propriétés physiques
        # ------------------------------------------------

        self.radius = FOOD.radius

        self.color = FOOD.color
        # Important pour :
        # SpatialGrid / Raycaster / Sensors

        self.type = FOOD.type


        # ------------------------------------------------
        # Valeur nutritive
        # ------------------------------------------------

        



        # Etat

        self.alive = True



    # ----------------------------------------------------
    # Consommation
    # ----------------------------------------------------

    def consume(self):

        """
        Marque la nourriture comme consommée.
        """

        self.alive = False



    # ----------------------------------------------------
    # Repositionnement
    # ----------------------------------------------------

    def respawn(
        self,
        width,
        height
    ):

        """
        Replace la nourriture ailleurs.
        """

        self.x = random.uniform(
            0,
            width
        )

        self.y = random.uniform(
            0,
            height
        )


        self.alive = True

    def setPos(self, x, y):
        self.x=x
        self.y=y
