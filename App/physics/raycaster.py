import math
#from App.physics.jit_math import ray_circle_test
#
# from App.physics.jit_math import raycast_objects
class Raycaster:


    def __init__(
        self,
        spatial_grid,
        world
    ):

        self.grid = spatial_grid

        self.world = world

        self.query_id = 0



   