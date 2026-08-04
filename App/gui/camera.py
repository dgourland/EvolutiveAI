"""
App/gui/camera.py

Gestion de la caméra OpenGL.

La caméra ne garde aucune référence
aux objets du monde.

Elle suit un index de créature.
"""

import math


class Camera:


    def __init__(self, width, height):
        # zoom
        self.zoom = 1.0


        # interpolation suivi
        self.follow_speed = 0.15


        # taille écran
        self.width = width
        self.height = height

        self.x = self.width*0.5
        self.y = self.height*0.5



    def resize(
        self,
        width,
        height
    ):

        self.width = width
        self.height = height



    def follow(
        self,
        spectator_id,
        world
    ):

        if spectator_id < 0:
            self.reset()
            return


        if spectator_id >= world.object_count:
            return


        target_x = world.object_data[0,spectator_id]
        target_y = world.object_y[spectator_id]


        self.x += (
            target_x - self.x
        ) * self.follow_speed


        self.y += (
            target_y - self.y
        ) * self.follow_speed



    def get_view_bounds(self):

        half_width = (
            self.width /
            (2 * self.zoom)
        )

        half_height = (
            self.height /
            (2 * self.zoom)
        )


        return (
            self.x - half_width,
            self.y - half_height,
            self.x + half_width,
            self.y + half_height
        )



    def world_to_screen(
        self,
        x,
        y
    ):

        sx = (
            x - self.x
        ) * self.zoom + self.width / 2


        sy = (
            y - self.y
        ) * self.zoom + self.height / 2


        return sx, sy



    def apply_zoom(
        self,
        delta
    ):

        self.zoom += delta


        if self.zoom < 0.1:
            self.zoom = 0.1


        if self.zoom > 20:
            self.zoom = 20



    def reset(self):

        self.x = self.width*0.5
        self.y = self.height*0.5
        self.zoom = 1.0