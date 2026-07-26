import pygame

from .colors import TEXT


class UI:


    def __init__(self):

        self.font = pygame.font.SysFont(
            "Arial",
            20
        )


    def draw(self, screen, app):


        data = [

            f"FPS: {app.fps:.1f}",

            f"UPS: {app.updates_per_second}",

            f"Simulation: {app.simulation_ms:.3f} ms",

            f"Render: {app.render_ms:.3f} ms",

            f"Creatures: {len(app.world.creatures)}",

            f"Food: {len(app.world.foods)}",

            f"Generation: {app.sim.generation}",

            f"Time: {app.world.time}",

        ]


        y = 10


        for line in data:


            text = self.font.render(
                line,
                True,
                TEXT
            )


            screen.blit(
                text,
                (10, y)
            )


            y += 25