import math
import pygame

from .colors import *

class Renderer:

    def __init__(self, screen, camera):

        self.screen = screen
        self.camera = camera

    def draw_sensor_rays(self, world, creature):

        sensor = world.sensor_system

        for relative_angle in sensor.ray_angles:

            angle = creature.angle + relative_angle

            hit = sensor.raycaster.cast(

                origin=(creature.x, creature.y),

                angle=angle,

                max_distance=sensor.max_distance,

                ignore=creature
            )

            x1, y1 = self.camera.world_to_screen(
                creature.x,
                creature.y
            )

            if hit is None:

                endx = (
                    creature.x
                    + math.cos(angle) * sensor.max_distance
                )

                endy = (
                    creature.y
                    + math.sin(angle) * sensor.max_distance
                )

                color = (255, 255, 255)

            else:

                endx = hit.x
                endy = hit.y

                if hit.object.type == 1:
                    color = (0,255,0)
                else:
                    color = (255,0,0)

            x2, y2 = self.camera.world_to_screen(endx, endy)

            pygame.draw.line(
                self.screen,
                color,
                (int(x1), int(y1)),
                (int(x2), int(y2)),
                1
            )
    def draw(self, world, spectator=None):

        self.screen.fill((80,80,80))
        

        self.draw_food(world)

        self.draw_creatures(world, spectator)

        if spectator is not None:
            self.draw_sensor_rays(world, spectator)

    def draw_food(self, world):

        for food in world.foods:

            x, y = self.camera.world_to_screen(food.x, food.y)

            pygame.draw.circle(
                self.screen,
                FOOD,
                (int(x), int(y)),
                max(2, int(food.radius*self.camera.zoom))
            )

    def draw_creatures(self, world, spectator=None):

        for c in world.creatures:

            x, y = self.camera.world_to_screen(c.x, c.y)

            radius = max(
                3,
                int(c.radius * self.camera.zoom)
            )

            pygame.draw.circle(
                self.screen,
                CREATURE,
                (int(x), int(y)),
                radius
            )

            # Halo jaune autour de la créature observée
            if c is spectator:

                pygame.draw.circle(
                    self.screen,
                    (255, 255, 0),
                    (int(x), int(y)),
                    radius + 4,
                    2
                )

            endx = x + math.cos(c.angle) * radius * 2
            endy = y + math.sin(c.angle) * radius * 2

            pygame.draw.line(
                self.screen,
                WHITE,
                (int(x), int(y)),
                (int(endx), int(endy)),
                2
            )