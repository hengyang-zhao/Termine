#!/usr/bin/env python3

import curses

import RC

from MineField import MineField

class MineFieldPane:

    def __init__(self, stdscr, width):

        self._mineField = None

        self._win = curses.newwin(curses.LINES - 1, width, 0, 0)
        self._win.border()

    def getMaxFieldSize(self):

        yMax, xMax = self._win.getmaxyx()
        return int((xMax - 11) / 4), int((yMax - 5) / 2)

    def allocateMineField(self, mfWidth, mfHeight):

        self._mineField = MineField(mfWidth, mfHeight)

    def refresh(self):

        self.redrawRulers()
        self.redrawMineField()
        self._win.refresh()

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

                if c == MineField.OPEN_CELL_0:
                    s = '0'
                elif c == MineField.OPEN_CELL_1:
                    s = '1'
                elif c == MineField.OPEN_CELL_2:
                    s = '2'
                elif c == MineField.OPEN_CELL_3:
                    s = '3'
                elif c == MineField.OPEN_CELL_4:
                    s = '4'
                elif c == MineField.OPEN_CELL_5:
                    s = '5'
                elif c == MineField.OPEN_CELL_6:
                    s = '6'
                elif c == MineField.OPEN_CELL_7:
                    s = '7'
                elif c == MineField.OPEN_CELL_8:
                    s = '8'
                elif c == MineField.FLAG_CELL:
                    s = 'F'
                elif c == MineField.BLANK_CELL:
                    s = ' '
                else:
                    pass # XXX: raise an exception!

                self._win.addstr(yStart + cellY * 2 + 1, xStart + cellX * 4 + 2, s)

class LogPane:

    def __init__(self, stdscr, width):

        self._win = curses.newwin(curses.LINES - 1, width, 0, curses.COLS - width)

        self._win.border()

    def refresh(self):
        self._win.refresh()

class BottomPane:

    def __init__(self, stdscr):

        self._win = curses.newwin(0, curses.COLS, curses.LINES - 1, 1)

    def refresh(self):
        self._win.refresh()

def Main(stdscr):
    stdscr.clear()

    mineFieldPane = MineFieldPane(stdscr, curses.COLS - RC.LOG_WINDOW_WIDTH)
    logPane = LogPane(stdscr, RC.LOG_WINDOW_WIDTH)
    bottomPane = BottomPane(stdscr)

    mfWidth, mfHeight = mineFieldPane.getMaxFieldSize()
    if mfWidth >= 30 and mfHeight >= 16:
        mineFieldPane.allocateMineField(30, 16)
    else:
        mineFieldPane.allocateMineField(mfWidth, mfHeight)

    stdscr.refresh()
    mineFieldPane.refresh()
    logPane.refresh()
    bottomPane.refresh()

    stdscr.getkey()
    mineFieldPane._mineField.setCell(10, 2, MineField.OPEN_CELL_6)

    stdscr.refresh()
    mineFieldPane.refresh()
    logPane.refresh()
    bottomPane.refresh()

    stdscr.getkey()

curses.wrapper(Main)
