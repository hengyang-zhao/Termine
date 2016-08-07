class MineField:

    OPEN_CELL_0 = 0
    OPEN_CELL_1 = 1
    OPEN_CELL_2 = 2
    OPEN_CELL_3 = 3
    OPEN_CELL_4 = 4
    OPEN_CELL_5 = 5
    OPEN_CELL_6 = 6
    OPEN_CELL_7 = 7
    OPEN_CELL_8 = 8
    FLAG_CELL = 9
    BLANK_CELL = 10

    def __init__(self, width, height):
        self._width = width
        self._height = height
        self._field = [MineField.BLANK_CELL for _ in range(width * height)]

    def getCell(self, x, y):
        return self._field[self._flatIndex(x, y)]

    def setCell(self, x, y, v):
        self._field[self._flatIndex(x, y)] = v

    def getSize(self):
        return self._width, self._height

    def _flatIndex(self, x, y):
        return self._width * y + x

