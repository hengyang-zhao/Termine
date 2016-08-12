import re
from collections import deque

from MineField import MineField
from MineField import MineDeployer

class Shell:

    def __init__(self):

        self._mineField = None
        self._minesCount = None
        self._isBoomed = False
        self._output = []

    def getOutput(self):

        return self._output

    def run(self, cmd):

        self._output = []

        args = self._parseMineField(cmd)
        if args is not None:
            self._doMineField(args)

        args = self._parsePoke(cmd)
        if args is not None:

            self._doPoke(args)
            return

        args = self._parsePeek(cmd)
        if args is not None:

            self._doPeek(args)
            return

        args = self._parseFlag(cmd)
        if args is not None:

            self._doFlag(args)
            return

        args = self._parseUnflag(cmd)
        if args is not None:

            self._doUnflag(args)
            return

        args = self._parseToggleFlag(cmd)
        if args is not None:

            self._doToggleFlag(args)
            return

        args = self._parseQuery(cmd)
        if args is not None:

            self._doQuery(args)
            return

    def _parseMineField(self, cmd):
        m = re.match(r"^\s*minefield\s+(\d+)\s+(\d+)\s+(\d+)\s*$", cmd)
        if m:
            args = {}
            args['width'] = int(m.group(1))
            args['height'] = int(m.group(2))
            args['mines'] = int(m.group(3))

            return args

        else:
            return None

    def _parsePoke(self, cmd):
        m = re.match(r"^\s*poke\s+(\d+)\s+(\d+)\s*$", cmd)

        if m:
            args = {}
            args['x'] = int(m.group(1))
            args['y'] = int(m.group(2))

            return args

        else:
            return None

    def _parseToggleFlag(self, cmd):
        m = re.match(r"^\s*toggle\s+(\d+)\s+(\d+)\s*$", cmd)

        if m:
            args = {}
            args['x'] = int(m.group(1))
            args['y'] = int(m.group(2))

            return args

        else:
            return None

    def _parseFlag(self, cmd):
        m = re.match(r"^\s*flag\s+(\d+)\s+(\d+)\s*$", cmd)

        if m:
            args = {}
            args['x'] = int(m.group(1))
            args['y'] = int(m.group(2))

            return args

        else:
            return None

    def _parseUnflag(self, cmd):
        m = re.match(r"^\s*unflag\s+(\d+)\s+(\d+)\s*$", cmd)

        if m:
            args = {}
            args['x'] = int(m.group(1))
            args['y'] = int(m.group(2))

            return args

        else:
            return None

    def _parsePeek(self, cmd):
        m = re.match(r"^\s*peek\s+(\d+)\s+(\d+)\s*$", cmd)

        if m:
            args = {}
            args['x'] = int(m.group(1))
            args['y'] = int(m.group(2))

            return args

        else:
            return None;

    def _parseQuery(self, cmd):
        m = re.match(r"^\s*query\s+(\w+)\s*$", cmd)

        if m:
            args = {}
            args['query'] = m.group(1)
            return args

        else:
            return None

    def _doMineField(self, args):

        self._mineField = MineField(args['width'], args['height'])
        self._minesCount = args['mines']
        self._isBoomed = False
        self._boomedMines = []

        self._output.append("created minefield %(width)d x %(height)d with %(mines)d mines" % args)

    def _hasValidMineField(self):
        if self._mineField is None:
            self._output.append("no minefield")
            return False

        return True

    def _notYetBoomed(self):

        if self._isBoomed is True:
            self._output.append("boomed minefield")
            return False

        return True

    def _doFlag(self, args):
        if self._hasValidMineField() is False or self._notYetBoomed() is False:
            return

        x, y = args['x'], args['y']
        if self._mineField.isRevealed(x, y):
            return

        if self._mineField.isFlagged(x, y):
            return

        self._mineField.flag(x, y)
        self._output.append('%d %d flagged' % (x, y))

    def _doToggleFlag(self, args):
        if self._hasValidMineField() is False or self._notYetBoomed() is False:
            return

        x, y = args['x'], args['y']
        if self._mineField.isRevealed(x, y):
            return

        if self._mineField.isFlagged(x, y):
            self._mineField.unflag(x, y)
            self._output.append('%d %d unflagged' % (x, y))
        else:
            self._mineField.flag(x, y)
            self._output.append('%d %d flagged' % (x, y))

    def _doUnflag(self, args):
        if self._hasValidMineField() is False or self._notYetBoomed() is False:
            return

        x, y = args['x'], args['y']
        if self._mineField.isRevealed(x, y):
            return

        if not self._mineField.isFlagged(x, y):
            return

        self._mineField.unflag(x, y)
        self._output.append('%d %d unflagged' % (x, y))

    def _doQuery(self, args):

        if self._hasValidMineField() is False:
            return

        query = args['query']
        if query == 'flags':
            self._output.append("%d" % self._mineField.getFlagsCount())
        elif query == 'mines':
            self._output.append("%d" % self._minesCount)
        elif query == 'width':
            width, _ = self._mineField.getSize()
            self._output.append("%d" % width)
        elif query == 'height':
            _, height = self._mineField.getSize()
            self._output.append("%d" % height)
        elif query == 'success':
            self._output.append("yes" if self._mineField.isFinished() else "no")
        elif query == 'boomed':
            self._output.append("yes" if self._isBoomed else "no")
        elif query == 'boomedlist':
            for x, y in self._boomedMines:
                self._output.append("%d %d" % (x, y))
        elif query == 'mineslist':
            if not self._isBoomed:
                self._output.append("secret")
            else:
                for x, y in self._mineField.getMines():
                    self._output.append("%d %d" % (x, y))
        else:
            self._output.append("null")

    def _doPoke(self, args):

        if self._hasValidMineField() is False or self._notYetBoomed() is False:
            return

        x, y = args['x'], args['y']
        if self._checkCoordinates(x, y) is False:
            return

        if not self._mineField.isDeployed():
            md = MineDeployer()
            md.deploy(self._mineField, self._minesCount, x, y)

        self._recursiveReveal(x, y)

    def _recursiveReveal(self, x, y):

        if self._mineField.isFlagged(x, y):
            return

        firstRoundXYs = []
        boomedXYs = []
        openedXYs = []
        zerosQueue = deque()

        # Calculate which cells will be poked the first round
        if self._mineField.isRevealed(x, y):
            # Poke a revealed cell
            if len(list(self._mineField.getFlaggedXYs(x, y))) == self._mineField.getDigit(x, y):
                for xx, yy in self._mineField.getUnrevealedXYs(x, y):
                    firstRoundXYs.append((xx, yy))
        else:
            # Poke an unrevealed cell
            firstRoundXYs.append((x, y))

        # Poke the cells on the first round
        for xx, yy in firstRoundXYs:
            dd = self._mineField.reveal(xx, yy)
            if dd is None:
                boomedXYs.append((xx, yy))
            else:
                openedXYs.append((xx, yy))
            if dd is 0:
                zerosQueue.append((xx, yy))

        # Something boomed
        if len(boomedXYs) is not 0:
            for xx, yy in boomedXYs:
                self._output.append('%d %d boomed' % (xx, yy))
                self._boomedMines.append((xx, yy))

            self._isBoomed = True
            return

        # Poke those cells with digit 0
        while len(zerosQueue) is not 0:
            xx, yy = zerosQueue.popleft()

            for xxx, yyy in self._mineField.getSurroundingXYs(xx, yy):

                # (xxx, yyy) is not a mine for sure
                if self._mineField.isRevealed(xxx, yyy):
                    continue

                if self._mineField.reveal(xxx, yyy) is 0:
                    zerosQueue.append((xxx, yyy))

                openedXYs.append((xxx, yyy))

        # Survived! Report the opened cells
        for xx, yy in openedXYs:
            self._output.append("%d %d opened as %d" % (xx, yy, self._mineField.getDigit(xx, yy)))

    def _checkCoordinates(self, x, y):
        xMax, yMax = self._mineField.getSize()
        if (x < 0 or y < 0 or x >= xMax or y >= yMax):
            self._output.append("out of bounds")
            return False

        return True

    def _doPeek(self, args):

        if self._hasValidMineField() is False:
            return

        x, y = args['x'], args['y']
        if self._checkCoordinates(x, y) is False:
            return

        if self._mineField.isRevealed(x, y):
            self._output.append("%d" % self._mineField.getDigit(x, y))
        elif self._mineField.isFlagged(x, y):
            self._output.append("flagged")
        else:
            self._output.append("unexplored")

