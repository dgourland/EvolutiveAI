"""
App/vars.py

Contient les classes statiques FOOD, PREY et PREDATOR,
contenant des paramètres afin de maitriser plus facilement les caractéristiques de chaque espèce.

"""

class FOOD:
    type=0
    radius=4

class PREY:
    type=1
    ray_count=20
    field_of_view=300
    max_distance=150
    radius=8

class PREDATOR:
    type=2
    ray_count=20
    field_of_view=90
    max_distance=250
    radius=8