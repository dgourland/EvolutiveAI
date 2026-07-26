"""
spatial_grid.py

Spatial Hash Grid pour simulation d'écosystème.

Permet de retrouver rapidement les objets proches
sans parcourir toutes les entités du monde.

Chaque objet doit posséder :

    obj.x
    obj.y
    obj.radius

Optionnel :

    obj.type

Exemple :
    "creature"
    "food"
    "obstacle"
"""


from collections import defaultdict


class SpatialGrid:

    def __init__(self, cell_size=64):

        """
        cell_size :
            taille d'une cellule en pixels.

        Une valeur entre 32 et 128 fonctionne
        généralement bien.
        """

        self.cell_size = cell_size

        # {(cell_x, cell_y): [objets]}
        self.cells = defaultdict(list)


    # --------------------------------------------------
    # Conversion coordonnées -> cellule
    # --------------------------------------------------

    def get_cell(self, x, y):

        return (
            int(x // self.cell_size),
            int(y // self.cell_size)
        )


    # --------------------------------------------------
    # Reset complet
    # --------------------------------------------------

    def clear(self):

        self.cells.clear()


    # --------------------------------------------------
    # Ajout d'un objet
    # --------------------------------------------------

    def insert(self, obj):

        """
        Ajoute un objet dans toutes les cellules
        qu'il occupe.
        """

        radius = obj.radius


        min_x = int(
            (obj.x - radius)
            // self.cell_size
        )

        max_x = int(
            (obj.x + radius)
            // self.cell_size
        )


        min_y = int(
            (obj.y - radius)
            // self.cell_size
        )

        max_y = int(
            (obj.y + radius)
            // self.cell_size
        )


        for cell_x in range(min_x, max_x + 1):

            for cell_y in range(min_y, max_y + 1):

                self.cells[
                    (cell_x, cell_y)
                ].append(obj)

    def query_cell(self, cell_x, cell_y):

        return self.cells.get(
            (cell_x, cell_y),
            ()
        )

    def ray_cells(
        self,
        x,
        y,
        dx,
        dy,
        max_distance
    ):

        step = self.cell_size * 0.32

        distance = 0

        visited = set()


        while distance <= max_distance:

            px = x + dx * distance
            py = y + dy * distance


            cell = self.get_cell(
                px,
                py
            )


            if cell not in visited:

                visited.add(cell)

                yield cell, distance


            distance += step
    # --------------------------------------------------
    # Reconstruction complète
    # --------------------------------------------------

    def rebuild(self, objects):

        """
        A appeler une fois par frame.

        Exemple :

            grid.rebuild(
                creatures + foods
            )
        """

        self.clear()


        for obj in objects:

            self.insert(obj)



    # --------------------------------------------------
    # Recherche locale
    # --------------------------------------------------

    def query(self, x, y):

        """
        Retourne les objets dans la cellule
        et les 8 cellules voisines.

        Utilisé par :
            - raycaster
            - collisions
            - IA
        """

        cell_x, cell_y = self.get_cell(x, y)


        results = []


        for x_offset in (-1, 0, 1):

            for y_offset in (-1, 0, 1):

                cell = (
                    cell_x + x_offset,
                    cell_y + y_offset
                )


                results.extend(
                    self.cells.get(
                        cell,
                        []
                    )
                )


        return results



    # --------------------------------------------------
    # Recherche dans un rayon
    # --------------------------------------------------

    def query_radius(
        self,
        x,
        y,
        radius
    ):

        """
        Retourne les objets réellement
        présents dans le cercle demandé.
        """

        results = []

        checked = set()


        min_x = int(
            (x-radius)
            // self.cell_size
        )

        max_x = int(
            (x+radius)
            // self.cell_size
        )


        min_y = int(
            (y-radius)
            // self.cell_size
        )

        max_y = int(
            (y+radius)
            // self.cell_size
        )


        radius_squared = radius * radius


        for cx in range(min_x, max_x+1):

            for cy in range(min_y, max_y+1):


                for obj in self.cells.get(
                    (cx, cy),
                    []
                ):

                    # éviter doublons
                    if id(obj) in checked:
                        continue


                    checked.add(id(obj))


                    dx = obj.x - x
                    dy = obj.y - y


                    if (
                        dx*dx + dy*dy
                        <= radius_squared
                    ):

                        results.append(obj)


        return results