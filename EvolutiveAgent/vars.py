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
    ray_count=32
    field_of_view=240
    max_distance=150
    radius=8
    memory_size=16
    metrics_size=5
    hidden1_layer=32
    hidden2_layer=32
    output_size=5
    
class PREDATOR:
    type=2
    ray_count=32
    field_of_view=120
    max_distance=250
    radius=8
    memory_size=16
    metrics_size=5
    hidden1_layer=32
    hidden2_layer=32
    output_size=5
    