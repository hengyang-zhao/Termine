#!/usr/bin/env python3

import curses
from collections import deque

import RC

from TUIMineField import TUIMineField
from Shell import Shell

class MineFieldPane:

    def __init__(self, stdscr, width):

        self._mineField = None

        self._win = curses.newwin(curses.LINES - 1, width, 0, 0)

    def getMaxFieldSize(self):

        yMax, xMax = self._win.getmaxyx()
        return int((xMax - 11) / 4), int((yMax - 5) / 2)

    def allocateMineField(self, mfWidth, mfHeight):

        self._mineField = TUIMineField(mfWidth, mfHeight)

    def refresh(self):

        self._win.clear()
        self._win.border()
        self.redrawRulers()
        self.redrawMineField()
        self._win.refresh()

    def retrieveMineFieldCoordinate(self, x, y):

        yMax, xMax = self._win.getmaxyx()
        mfWidth, mfHeight = self._mineField.getSize()

        xStart = int((xMax - (mfWidth * 4 + 1)) / 2)
        yStart = int((yMax - (mfHeight * 2 + 1)) / 2)

        xEnd = xStart + mfWidth * 4
        yEnd = yStart + mfWidth * 2

        if x < xStart or y < yStart or x >= xEnd or y >= yEnd or (x - xStart) % 4 == 0 or (y - yStart) % 2 == 0:
            return None

        return (x - xStart) // 4, (y - yStart) // 2

    def redrawRulers(self):

        if self._mineField is None:
            return

        yMax, xMax = self._win.getmaxyx()
        mfWidth, mfHeight = self._mineField.getSize()

        xStart = int((xMax - (mfWidth * 4 + 1)) / 2)
        yStart = int((yMax - (mfHeight * 2 + 1)) / 2)

        for x in range(mfWidth):
            self._win.addstr(yStart - 1, xStart + x * 4 + 2 - len(str(x)) // 2, str(x))
            self._win.addstr(yStart + mfHeight * 2 + 1, xStart + x * 4 + 2 - len(str(x)) // 2, str(x))

        for y in range(mfHeight):
            self._win.addstr(yStart + 2 * y + 1, xStart - 1 - len(str(y)), str(y))
            self._win.addstr(yStart + 2 * y + 1, xStart + mfWidth * 4 + 2, str(y))

    def update(self, shell):
        xMax, yMax = self._mineField.getSize()
        for x in range(xMax):
            for y in range(yMax):
                shell.run("peek %d %d" % (x, y))

                answer = shell.getOutput()[0]
                if answer == "flagged":
                    self._mineField.setCell(x, y, TUIMineField.FLAG_CELL)
                elif answer == "unexplored":
                    self._mineField.setCell(x, y, TUIMineField.BLANK_CELL)
                else:
                    self._mineField.setCell(x, y, int(answer))

    def redrawMineField(self):

        if self._mineField is None:
            return

        yMax, xMax = self._win.getmaxyx()
        mfWidth, mfHeight = self._mineField.getSize()

        xStart = int((xMax - (mfWidth * 4 + 1)) / 2)
        yStart = int((yMax - (mfHeight * 2 + 1)) / 2)

        for cellX in range(mfWidth):
            for cellY in range(mfHeight):
                self._win.addstr(yStart + cellY * 2, xStart + cellX * 4, '+')
                self._win.addstr(yStart + cellY * 2, xStart + cellX * 4 + 1, '-')
                self._win.addstr(yStart + cellY * 2, xStart + cellX * 4 + 2, '-')
                self._win.addstr(yStart + cellY * 2, xStart + cellX * 4 + 3, '-')
                self._win.addstr(yStart + cellY * 2, xStart + cellX * 4 + 4, '+')
                self._win.addstr(yStart + cellY * 2 + 1, xStart + cellX * 4, '|')
                self._win.addstr(yStart + cellY * 2 + 1, xStart + cellX * 4 + 4, '|')
                self._win.addstr(yStart + cellY * 2 + 2, xStart + cellX * 4, '+')
                self._win.addstr(yStart + cellY * 2 + 2, xStart + cellX * 4 + 1, '-')
                self._win.addstr(yStart + cellY * 2 + 2, xStart + cellX * 4 + 2, '-')
                self._win.addstr(yStart + cellY * 2 + 2, xStart + cellX * 4 + 3, '-')
                self._win.addstr(yStart + cellY * 2 + 2, xStart + cellX * 4 + 4, '+')

                c = self._mineField.getCell(cellX, cellY)
                s = None

                if c == TUIMineField.OPEN_CELL_0:
                    s = '0'
                elif c == TUIMineField.OPEN_CELL_1:
                    s = '1'
                elif c == TUIMineField.OPEN_CELL_2:
                    s = '2'
                elif c == TUIMineField.OPEN_CELL_3:
                    s = '3'
                elif c == TUIMineField.OPEN_CELL_4:
                    s = '4'
                elif c == TUIMineField.OPEN_CELL_5:
                    s = '5'
                elif c == TUIMineField.OPEN_CELL_6:
                    s = '6'
                elif c == TUIMineField.OPEN_CELL_7:
                    s = '7'
                elif c == TUIMineField.OPEN_CELL_8:
                    s = '8'
                elif c == TUIMineField.FLAG_CELL:
                    s = 'F'
                elif c == TUIMineField.BLANK_CELL:
                    s = ' '
                else:
                    pass # XXX: raise an exception!

                self._win.addstr(yStart + cellY * 2 + 1, xStart + cellX * 4 + 2, s)

class LogPane:

    def __init__(self, stdscr, width):

        self._win = curses.newwin(curses.LINES - 1, width, 0, curses.COLS - width)
        self._logLines = deque()

    def push(self, s):

        self._logLines.append(s)

    def printLog(self):

        while len(self._logLines) > self._maxLines():
            self._logLines.popleft()

        y, x = self._win.getyx()
        for line in self._logLines:
            self._win.addstr(y + 1, x + 1, line)
            y += 1

    def refresh(self):

        self._win.clear()

        self.printLog()

        self._win.border()
        self._win.refresh()

    def _maxLines(self):
        yMax, xMax = self._win.getmaxyx()
        return yMax - 2

class BottomPane:

    def __init__(self, stdscr):

        self._win = curses.newwin(0, curses.COLS, curses.LINES - 1, 1)

    def refresh(self):
        self._win.refresh()

def Main(stdscr):
    stdscr.clear()
    curses.mousemask(curses.BUTTON1_CLICKED | curses.BUTTON3_CLICKED)

    mineFieldPane = MineFieldPane(stdscr, curses.COLS - RC.LOG_WINDOW_WIDTH)
    logPane = LogPane(stdscr, RC.LOG_WINDOW_WIDTH)
    bottomPane = BottomPane(stdscr)
    shell = Shell()

    mfWidth, mfHeight = mineFieldPane.getMaxFieldSize()
    if mfWidth >= 30 and mfHeight >= 16:
        mineFieldPane.allocateMineField(30, 16)
        shell.run("minefield %d %d %d" % (30, 16, 100))
    else:
        mineFieldPane.allocateMineField(mfWidth, mfHeight)
        shell.run("minefield %d %d %d" % (mfWidth, mfHeight, mfWidth * mfHeight // 10))

    stdscr.refresh()
    mineFieldPane.refresh()
    logPane.refresh()
    bottomPane.refresh()

    while True:
        event = stdscr.getch()

        if event == curses.KEY_MOUSE:
            mouseEvent = curses.getmouse()
            _, mx, my, _, btn = mouseEvent
            coor = mineFieldPane.retrieveMineFieldCoordinate(mx, my)
            logPane.push(str(mouseEvent))

            if coor is None:
                continue

            if btn == curses.BUTTON1_CLICKED:
                x, y = coor
                logPane.push("poke %d %d" % (x, y))
                shell.run("poke %d %d" % (x, y))
                for line in shell.getOutput():
                    logPane.push(line)
            elif btn == curses.BUTTON3_CLICKED:
                x, y = coor
                logPane.push("toggle %d %d" % (x, y))
                shell.run("toggle %d %d" % (x, y))
                for line in shell.getOutput():
                    logPane.push(line)
            else:
                logPane.push("btn == %d" % btn)
                logPane.push("BUTTON1_CLICKED == %d" % curses.BUTTON1_CLICKED)
                logPane.push("BUTTON3_CLICKED == %d" % curses.BUTTON3_CLICKED)
                pass

        mineFieldPane.update(shell)

        stdscr.refresh()
        mineFieldPane.refresh()
        logPane.refresh()
        bottomPane.refresh()

curses.wrapper(Main)
