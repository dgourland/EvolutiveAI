class Camera:

    def __init__(self):

        self.x = 0
        self.y = 0

        self.zoom = 1.0
        
    def follow(self, target, screen_width, screen_height):

        self.x = target.x - screen_width / 2 / self.zoom
        self.y = target.y - screen_height / 2 / self.zoom


    def world_to_screen(self, x, y):

        sx = (x - self.x) * self.zoom
        sy = (y - self.y) * self.zoom

        return sx, sy