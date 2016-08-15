import random

class MineField:

    def __init__(self, width, height):
        self._width = width
        self._height = height

        self.clear()

    def isMine(self, x, y):
        return (x, y) in self._mines

    def isFlagged(self, x, y):
        return (x, y) in self._flagged

    def isRevealed(self, x, y):
        return (x, y) in self._revealed

    def isDeployed(self):
        return self._deployed

    def reveal(self, x, y):
        if (x, y) in self._mines:
            return None
        self._flagged.discard((x, y))
        self._revealed.add((x, y))

        return self.getDigit(x, y)

    def flag(self, x, y):
        if (x, y) in self._revealed:
            return

        self._flagged.add((x, y))

    def unflag(self, x, y):
        self._flagged.discard((x, y))

    def getSize(self):
        return (self._width, self._height)

    def getDigit(self, x, y):

        ret = 0
        for xx, yy in self.getSurroundingXYs(x, y):
            if self.isMine(xx, yy):
                ret += 1

        return ret

    def getMines(self):
        for x, y in self._mines:
            yield x, y

    def getFlags(self):
        for x, y in self._flagged:
            yield x, y

    def getFalseFlags(self):
        for x, y in set(self.getFlags()).difference(set(self.getMines())):
            yield x, y

    def getMinesCount(self):
        return len(self._mines)

    def getFlagsCount(self):
        return len(self._flagged)

    def getRevealed(self):
        for (x, y) in self._revealed:
            yield x, y

    def getUnexplored(self):
        for x in range(self._width):
            for y in range(self._height):
                if (x, y) not in self._flagged and (x, y) not in self._revealed:
                    yield x, y

    def isFinished(self):
        return len(self._revealed) + len(self._mines) == self._width * self._height

    def deployMine(self, x, y):
        self._mines.add((x, y))

    def clear(self, keepFlags=False):
        self._mines = set()
        self._revealed = set()

        if keepFlags is False:
            self._flagged = set()

        self._deployed = False

    def _flatIndex(self, x, y):
        return self._width * y + x

    def getSurroundingXYs(self, x, y):
        for xx in (x - 1, x, x + 1):
            for yy in (y - 1, y, y + 1):
                if xx == x and yy == y: continue
                if xx < 0 or xx >= self._width: continue
                if yy < 0 or yy >= self._height: continue

                yield (xx, yy)

    def getFlaggedXYs(self, x, y):
        for xx, yy in self.getSurroundingXYs(x, y):
            if self.isFlagged(xx, yy):
                yield (xx, yy)

    def getUnrevealedXYs(self, x, y):
        for xx, yy in self.getSurroundingXYs(x, y):
            if not self.isFlagged(xx, yy) and not self.isRevealed(xx, yy):
                yield (xx, yy)

class MineDeployer:

    def deploy(self, mineField, nMines, x, y, seed=None):

        width, height = mineField.getSize()

        possibleMines = set([(i, j)
                for i in range(width)
                for j in range(height)])

        possibleMines.discard((x, y))
        for i, j in mineField.getSurroundingXYs(x, y):
            possibleMines.discard((i, j))

        rnd = random.Random()
        if seed is not None:
            rnd.seed(seed)

        mineField.clear(keepFlags=True)
        for (i, j) in rnd.sample(possibleMines, nMines):
            mineField.deployMine(i, j)

        mineField._deployed = True

