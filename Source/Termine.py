#!/usr/bin/env python3

import curses
from collections import deque

import RC
import Shell

class MineFieldWindow:

    def __init__(self, screen, width, shell):

        self._win = curses.newwin(curses.LINES, width, 0, 0)
        self._shell = shell

    def getMaxMineFieldSize(self):

        cHeight, cWidth = self._win.getmaxyx()
        mfWidth = (cWidth - (RC.MINE_FIELD_MARGIN_CWIDTH + RC.MINE_FIELD_BORDER_CWIDTH) * 2 - 1) // (RC.MINE_FIELD_CELL_CWIDTH + 1)
        mfHeight = (cHeight - (RC.MINE_FIELD_MARGIN_CHEIGHT + RC.MINE_FIELD_BORDER_CHEIGHT) * 2 - 1) // (RC.MINE_FIELD_CELL_CHEIGHT + 1)

        return mfWidth, mfHeight

    def updateAll(self):

        self._win.erase()
        self._win.border()
        self.redrawMineField()
        self._win.refresh()

    def retrieveMineFieldCoordinate(self, cX, cY):

        xCStart, yCStart = self._mineFieldXYCStart()
        xCEnd, yCEnd = self._mineFieldYXCEnd()

        if cX < xCStart or cY < yCStart or cX >= xCEnd or cY >= yCEnd or (cX - xCStart) % (RC.MINE_FIELD_CELL_CWIDTH + 1) == 0 or (cY - yCStart) % (RC.MINE_FIELD_CELL_CHEIGHT + 1) == 0:
            return None

        return (cX - xCStart) // 4, (cY - yCStart) // 2

    def redrawMineField(self):

        mfWidth, mfHeight = self.currentMineFieldSize()

        for mfX in range(mfWidth):
            for mfY in range(mfHeight):
                self.redrawMineCell(mfX, mfY)

    def redrawMineCell(self, mfX, mfY):

        cell = self.cellAt(mfX, mfY)

        xCStart, yCStart = self._mineFieldXYCStart()
        mfWidth, mfHeight = self.currentMineFieldSize()

        if mfX == 0 and mfY == 0:
            ulCorner = curses.ACS_ULCORNER
        elif mfX == 0:
            ulCorner = curses.ACS_LTEE
        elif mfY == 0:
            ulCorner = curses.ACS_TTEE
        else:
            ulCorner = curses.ACS_PLUS

        if mfX + 1 >= mfWidth and mfY == 0:
            urCorner = curses.ACS_URCORNER
        elif mfX + 1 >= mfWidth:
            urCorner = curses.ACS_RTEE
        elif mfY == 0:
            urCorner = curses.ACS_TTEE
        else:
            urCorner = curses.ACS_PLUS

        if mfX == 0 and mfY + 1 >= mfHeight:
            llCorner = curses.ACS_LLCORNER
        elif mfX == 0:
            llCorner = curses.ACS_LTEE
        elif mfY + 1 >= mfHeight:
            llCorner = curses.ACS_BTEE
        else:
            llCorner = curses.ACS_PLUS

        if mfX + 1 >= mfWidth and mfY + 1 >= mfHeight:
            lrCorner = curses.ACS_LRCORNER
        elif mfX + 1 >= mfWidth:
            lrCorner = curses.ACS_RTEE
        elif mfY + 1 >= mfHeight:
            lrCorner = curses.ACS_BTEE
        else:
            lrCorner = curses.ACS_PLUS

        self._win.addch(yCStart + mfY * (RC.MINE_FIELD_CELL_CHEIGHT + 1), xCStart + mfX * (RC.MINE_FIELD_CELL_CWIDTH + 1), ulCorner)
        self._win.addch(yCStart + mfY * (RC.MINE_FIELD_CELL_CHEIGHT + 1), xCStart + (mfX + 1) * (RC.MINE_FIELD_CELL_CWIDTH + 1), urCorner)
        self._win.addch(yCStart + (mfY + 1) * (RC.MINE_FIELD_CELL_CHEIGHT + 1), xCStart + mfX * (RC.MINE_FIELD_CELL_CWIDTH + 1), llCorner)
        self._win.addch(yCStart + (mfY + 1) * (RC.MINE_FIELD_CELL_CHEIGHT + 1), xCStart + (mfX + 1) * (RC.MINE_FIELD_CELL_CWIDTH + 1), lrCorner)

        for x in range(1, RC.MINE_FIELD_CELL_CWIDTH + 1):
            self._win.addch(yCStart + mfY * (RC.MINE_FIELD_CELL_CHEIGHT + 1), xCStart + mfX * (RC.MINE_FIELD_CELL_CWIDTH + 1) + x, curses.ACS_HLINE)
            self._win.addch(yCStart + (mfY + 1) * (RC.MINE_FIELD_CELL_CHEIGHT + 1), xCStart + mfX * (RC.MINE_FIELD_CELL_CWIDTH + 1) + x, curses.ACS_HLINE)

        for y in range(1, RC.MINE_FIELD_CELL_CHEIGHT + 1):
            self._win.addch(yCStart + mfY * (RC.MINE_FIELD_CELL_CHEIGHT + 1) + y, xCStart + mfX * (RC.MINE_FIELD_CELL_CWIDTH + 1), curses.ACS_VLINE)
            self._win.addch(yCStart + mfY * (RC.MINE_FIELD_CELL_CHEIGHT + 1) + y, xCStart + (mfX + 1) * (RC.MINE_FIELD_CELL_CWIDTH + 1), curses.ACS_VLINE)


        self._win.addstr(yCStart + mfY * (RC.MINE_FIELD_CELL_CHEIGHT + 1) + 1, xCStart + mfX * (RC.MINE_FIELD_CELL_CWIDTH + 1) + 1, cell.text(), cell.attr())

    def currentMineFieldSize(self):

        self._shell.run("query width")
        mfWidth = int(list(self._shell.getOutput())[0])

        self._shell.run("query height")
        mfHeight = int(list(self._shell.getOutput())[0])

        return mfWidth, mfHeight

    def isBoomed(self):
        self._shell.run('query boomed')
        return list(self._shell.getOutput())[0] == 'yes'

    def cellAt(self, mfX, mfY):

        self._shell.run("peek %d %d" % (mfX, mfY))
        cell = list(self._shell.getOutput())[0]

        if cell == '0':
            return RC.CELL_DIGIT_NONE
        elif cell == '1':
            return RC.CELL_DIGIT_1
        elif cell == '2':
            return RC.CELL_DIGIT_2
        elif cell == '3':
            return RC.CELL_DIGIT_3
        elif cell == '4':
            return RC.CELL_DIGIT_4
        elif cell == '5':
            return RC.CELL_DIGIT_5
        elif cell == '6':
            return RC.CELL_DIGIT_6
        elif cell == '7':
            return RC.CELL_DIGIT_7
        elif cell == '8':
            return RC.CELL_DIGIT_8
        elif cell == 'unexplored':
            return RC.CELL_UNEXPLORED
        elif cell == 'flagged' or cell == 'trueflag':
            return RC.CELL_FLAGGED
        elif cell == 'falseflag':
            return RC.CELL_WRONG
        elif cell == 'boomed':
            return RC.CELL_BOOMED
        elif cell == 'mine':
            return RC.CELL_UNFLAGGED_MINE
        else:
            raise Exception("Unknown cell type: %s" % cell) 

    def _mineFieldXYCStart(self):

        cHeight, cWidth = self._win.getmaxyx()
        mfWidth, mfHeight = self.currentMineFieldSize()

        xCStart = (cWidth - (mfWidth * (RC.MINE_FIELD_CELL_CWIDTH + 1) + 1)) // 2
        yCStart = (cHeight - (mfHeight * (RC.MINE_FIELD_CELL_CHEIGHT + 1) + 1)) // 2

        return xCStart, yCStart

    def _mineFieldYXCEnd(self):

        mfWidth, mfHeight = self.currentMineFieldSize()
        xCStart, yCStart = self._mineFieldXYCStart()

        xCEnd = xCStart + mfWidth * (RC.MINE_FIELD_CELL_CWIDTH + 1)
        yCEnd = yCStart + mfHeight * (RC.MINE_FIELD_CELL_CHEIGHT + 1)

        return xCEnd, yCEnd

class LogWindow:

    def __init__(self, screen, width, shell):

        self._win = curses.newwin(curses.LINES - 1, width, 0, curses.COLS - width)
        self._shell = shell
        self._logLines = deque()

    def push(self, s):

        self._logLines.append(s)

    def printLog(self):

        self._win.erase()

        while len(self._logLines) > self._maxLines():
            self._logLines.popleft()

        y, x = self._win.getyx()
        for line in self._logLines:
            self._win.addstr(y + 1, x + 1, line)
            y += 1

        self._win.border()

    def updateAll(self):

        self.printLog()

        self._win.refresh()

    def _maxLines(self):
        cHeight, _ = self._win.getmaxyx()
        return cHeight - RC.LOG_BORDER_CHEIGHT * 2

MINE_FIELD_WINDOW = None
LOG_WINDOW = None
SHELL = None

class EventLoop:

    def __init__(self, screen):
        self._screen = screen

    def mineFieldOnMouseClick(self, mX, mY, btn):

        coor = MINE_FIELD_WINDOW.retrieveMineFieldCoordinate(mX, mY)
        LOG_WINDOW.push("%d %d %d" % (mX, mY, btn))

        if coor is None:
            return

        if btn == curses.BUTTON1_PRESSED:
            x, y = coor
            LOG_WINDOW.push("poke %d %d" % (x, y))
            SHELL.run("poke %d %d" % (x, y))
            for line in SHELL.getOutput():
                LOG_WINDOW.push(line)
        elif btn == curses.BUTTON3_PRESSED:
            x, y = coor
            LOG_WINDOW.push("toggle %d %d" % (x, y))
            SHELL.run("toggle %d %d" % (x, y))
            for line in SHELL.getOutput():
                LOG_WINDOW.push(line)
        else:
            pass

    def newGameButtonOnMouseClick(self, mX, mY, btn):
        pass

    def pauseGameButtonOnMouseClick(self, mX, mY, btn):
        pass

    def bestRecordButtonOnMouseClick(self, mX, mY, btn):
        pass

    def run(self):

        global MINE_FIELD_WINDOW
        global LOG_WINDOW

        while True:

            event = self._screen.getch()

            if event == curses.KEY_MOUSE:
                mouseEvent = curses.getmouse()
                _, mX, mY, _, btn = mouseEvent

                self.mineFieldOnMouseClick(mX, mY, btn)

            MINE_FIELD_WINDOW.updateAll()
            LOG_WINDOW.updateAll()
            curses.doupdate()

def InitColor():
    curses.init_pair(0, curses.COLOR_BLACK, -1)
    curses.init_pair(1, curses.COLOR_RED, -1)
    curses.init_pair(2, curses.COLOR_GREEN, -1)
    curses.init_pair(3, curses.COLOR_YELLOW, -1)
    curses.init_pair(4, curses.COLOR_BLUE, -1)
    curses.init_pair(5, curses.COLOR_MAGENTA, -1)
    curses.init_pair(6, curses.COLOR_CYAN, -1)
    curses.init_pair(7, curses.COLOR_WHITE, -1)

def InitCurses():

    if (curses.has_colors()):
        curses.start_color()
        curses.use_default_colors()
        InitColor()

    curses.mousemask(curses.BUTTON1_PRESSED | curses.BUTTON3_PRESSED)
    curses.mouseinterval(0)
    curses.curs_set(False)

def Main(stdscr):

    global MINE_FIELD_WINDOW
    global LOG_WINDOW
    global SHELL

    InitCurses()

    stdscr.clear()

    SHELL = Shell.Shell()
    MINE_FIELD_WINDOW = MineFieldWindow(stdscr, curses.COLS - RC.LOG_WINDOW_WIDTH, SHELL)
    LOG_WINDOW = LogWindow(stdscr, RC.LOG_WINDOW_WIDTH, SHELL)

    mfWidthMax, mfHeightMax = MINE_FIELD_WINDOW.getMaxMineFieldSize()
    if mfWidthMax >= RC.MINE_FIELD_WIDTH and mfHeightMax >= RC.MINE_FIELD_HEIGHT:
        SHELL.run("minefield %d %d %d" % (RC.MINE_FIELD_WIDTH, RC.MINE_FIELD_HEIGHT, RC.MINE_FIELD_MINES))
    else:
        SHELL.run("minefield %d %d %d" % (mfWidthMax, mfHeightMax, int(mfWidthMax * mfHeightMax * RC.MINE_FIELD_DEFAULT_MINES_PERCENTAGE)))

    EventLoop(stdscr).run()

curses.wrapper(Main)
