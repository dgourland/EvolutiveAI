from collections import defaultdict
import math


class SpatialGrid:
    """
    Spatial Hash Grid

    Chaque objet est stocké dans une ou plusieurs cellules.
    Les capteurs peuvent ensuite ne récupérer que les objets proches.
    """

    def __init__(self, cell_size=64):

        self.cell_size = cell_size

        # {(cell_x, cell_y): [obj1, obj2, ...]}
        self.cells = defaultdict(list)

    # ---------------------------------------------------------
    # Internal
    # ---------------------------------------------------------

    def _cell(self, x, y):
        return (
            int(x // self.cell_size),
            int(y // self.cell_size)
        )

    # ---------------------------------------------------------
    # Public
    # ---------------------------------------------------------

    def clear(self):
        self.cells.clear()

    # ---------------------------------------------------------

    def insert(self, obj):
        """
        Ajoute un objet dans toutes les cellules qu'il recouvre.
        """

        r = obj.radius

        min_x = int((obj.x - r) // self.cell_size)
        max_x = int((obj.x + r) // self.cell_size)

        min_y = int((obj.y - r) // self.cell_size)
        max_y = int((obj.y + r) // self.cell_size)

        for gx in range(min_x, max_x + 1):
            for gy in range(min_y, max_y + 1):

                self.cells[(gx, gy)].append(obj)

    # ---------------------------------------------------------

    def rebuild(self, objects):
        """
        Reconstruit entièrement la grille.

        A appeler une fois par frame.
        """

        self.clear()

        for obj in objects:
            self.insert(obj)

    # ---------------------------------------------------------

    def query(self, x, y):
        """
        Retourne les objets de la cellule contenant (x,y)
        ainsi que des 8 cellules voisines.
        """

        cx, cy = self._cell(x, y)

        result = []

        for gx in range(cx - 1, cx + 2):
            for gy in range(cy - 1, cy + 2):

                result.extend(
                    self.cells.get((gx, gy), [])
                )

        return result

    # ---------------------------------------------------------

    def query_radius(self, x, y, radius):
        """
        Retourne uniquement les objets situés
        dans un rayon donné.
        """

        result = []

        min_x = int((x - radius) // self.cell_size)
        max_x = int((x + radius) // self.cell_size)

        min_y = int((y - radius) // self.cell_size)
        max_y = int((y + radius) // self.cell_size)

        r2 = radius * radius

        seen = set()

        for gx in range(min_x, max_x + 1):
            for gy in range(min_y, max_y + 1):

                for obj in self.cells.get((gx, gy), []):

                    if id(obj) in seen:
                        continue

                    seen.add(id(obj))

                    dx = obj.x - x
                    dy = obj.y - y

                    if dx * dx + dy * dy <= r2:

                        result.append(obj)

        return result

    # ---------------------------------------------------------

    def remove(self, obj):
        """
        Retire un objet de toutes les cellules.
        """

        r = obj.radius

        min_x = int((obj.x - r) // self.cell_size)
        max_x = int((obj.x + r) // self.cell_size)

        min_y = int((obj.y - r) // self.cell_size)
        max_y = int((obj.y + r) // self.cell_size)

        for gx in range(min_x, max_x + 1):
            for gy in range(min_y, max_y + 1):

                cell = self.cells.get((gx, gy))

                if cell is None:
                    continue

                try:
                    cell.remove(obj)
                except ValueError:
                    pass