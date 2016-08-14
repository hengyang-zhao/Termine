#!/usr/bin/env python3

import curses
import datetime
import threading
import time

from collections import deque
from collections import OrderedDict

import RC
import Shell

MINE_FIELD_WINDOW = None
STATUS_WINDOW = None
LOG_WINDOW = None
SHELL = None
ROOT_SCREEN = None

class MineFieldWindow:

    def __init__(self, width):

        self._win = curses.newwin(curses.LINES - 1, width, 0, 0)

    def getMaxMineFieldSize(self):

        cHeight, cWidth = self._win.getmaxyx()
        mfWidth = (cWidth - (RC.MINE_FIELD_MARGIN_CWIDTH + RC.MINE_FIELD_BORDER_CWIDTH) * 2 - 1) // (RC.MINE_FIELD_CELL_CWIDTH + 1)
        mfHeight = (cHeight - (RC.MINE_FIELD_MARGIN_CHEIGHT + RC.MINE_FIELD_BORDER_CHEIGHT) * 2 - 1) // (RC.MINE_FIELD_CELL_CHEIGHT + 1)

        return mfWidth, mfHeight

    def updateAll(self):

        self._win.erase()
        self._win.border()
        self.redrawMineField()
        self._win.noutrefresh()

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

        if self.isBoomed():
            borderStyle = RC.MINE_FIELD_BORDER_BOOMED_STYLE.attr()
        elif self.isFinished():
            borderStyle = RC.MINE_FIELD_BORDER_FINISHED_STYLE.attr()
        else:
            borderStyle = RC.MINE_FIELD_BORDER_DEFAULT_STYLE.attr()

        self._win.addch(yCStart + mfY * (RC.MINE_FIELD_CELL_CHEIGHT + 1), xCStart + mfX * (RC.MINE_FIELD_CELL_CWIDTH + 1), ulCorner, borderStyle)
        self._win.addch(yCStart + mfY * (RC.MINE_FIELD_CELL_CHEIGHT + 1), xCStart + (mfX + 1) * (RC.MINE_FIELD_CELL_CWIDTH + 1), urCorner, borderStyle)
        self._win.addch(yCStart + (mfY + 1) * (RC.MINE_FIELD_CELL_CHEIGHT + 1), xCStart + mfX * (RC.MINE_FIELD_CELL_CWIDTH + 1), llCorner, borderStyle)
        self._win.addch(yCStart + (mfY + 1) * (RC.MINE_FIELD_CELL_CHEIGHT + 1), xCStart + (mfX + 1) * (RC.MINE_FIELD_CELL_CWIDTH + 1), lrCorner, borderStyle)

        for x in range(1, RC.MINE_FIELD_CELL_CWIDTH + 1):
            self._win.addch(yCStart + mfY * (RC.MINE_FIELD_CELL_CHEIGHT + 1), xCStart + mfX * (RC.MINE_FIELD_CELL_CWIDTH + 1) + x, curses.ACS_HLINE, borderStyle)
            self._win.addch(yCStart + (mfY + 1) * (RC.MINE_FIELD_CELL_CHEIGHT + 1), xCStart + mfX * (RC.MINE_FIELD_CELL_CWIDTH + 1) + x, curses.ACS_HLINE, borderStyle)

        for y in range(1, RC.MINE_FIELD_CELL_CHEIGHT + 1):
            self._win.addch(yCStart + mfY * (RC.MINE_FIELD_CELL_CHEIGHT + 1) + y, xCStart + mfX * (RC.MINE_FIELD_CELL_CWIDTH + 1), curses.ACS_VLINE, borderStyle)
            self._win.addch(yCStart + mfY * (RC.MINE_FIELD_CELL_CHEIGHT + 1) + y, xCStart + (mfX + 1) * (RC.MINE_FIELD_CELL_CWIDTH + 1), curses.ACS_VLINE, borderStyle)


        self._win.addstr(yCStart + mfY * (RC.MINE_FIELD_CELL_CHEIGHT + 1) + 1, xCStart + mfX * (RC.MINE_FIELD_CELL_CWIDTH + 1) + 1, cell.text(), cell.attr())

    def currentMineFieldSize(self):

        SHELL.run("query width")
        mfWidth = int(next(SHELL.getOutput()))

        SHELL.run("query height")
        mfHeight = int(next(SHELL.getOutput()))

        return mfWidth, mfHeight

    def isBoomed(self):
        SHELL.run('query boomed')
        return next(SHELL.getOutput()) == 'yes'

    def isFinished(self):
        SHELL.run('query success')
        return next(SHELL.getOutput()) == 'yes'

    def cellAt(self, mfX, mfY):

        SHELL.run("peek %d %d" % (mfX, mfY))
        cell = next(SHELL.getOutput())

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

class StatusWindow:

    BUTTON_NEW_GAME = 0
    BUTTON_PAUSE = 1
    BUTTON_RECORDS = 2

    def __init__(self, width):
        self._win = curses.newwin(1, width, curses.LINES - 1, 0)
        self._startTime = None
        self._elapsedTime = None
        self._buttons = OrderedDict({
                StatusWindow.BUTTON_NEW_GAME: RC.BUTTON_NEW_GAME,
                StatusWindow.BUTTON_PAUSE: RC.BUTTON_PAUSE,
                StatusWindow.BUTTON_RECORDS: RC.BUTTON_RECORDS
                })

    def isTimerReset(self):
        return self._startTime is None and self._elapsedTime is None

    def startTimer(self):
        self._startTime = datetime.datetime.now()
        self._elapsedTime = None

    def resetTimer(self):
        self._startTime = None
        self._elapsedTime = None

    def stopTimer(self):
        assert self._startTime is not None
        if self._elapsedTime is None:
            self._elapsedTime = datetime.datetime.now() - self._startTime

    def clockString(self):
        if self._startTime is None:
            return "00:00.0"

        elapsed = self._elapsedTime if self._elapsedTime is not None else datetime.datetime.now() - self._startTime

        nmins = elapsed.seconds // 60
        nsecs = elapsed.seconds % 60
        ntenth = elapsed.microseconds // 100000

        if (nmins > 99):
            nmins = 99
            nsecs = 99
            ntenth = 9

        return "%02d:%02d.%01d" % (nmins, nsecs, ntenth)

    def progressString(self):
        SHELL.run("query flags")
        nFlags = next(SHELL.getOutput())
        SHELL.run("query mines")
        nMines = next(SHELL.getOutput())

        return "%s flags / %s mines" % (nFlags, nMines)

    def drawStatus(self, clockOnly=False):
        _, cWidth = self._win.getmaxyx()

        timeStr = RC.TIMER.text() % self.clockString()
        self._win.addstr(0, cWidth - len(timeStr) - 1, timeStr, RC.TIMER.attr())

        if clockOnly is True: return

        cWidth -= len(timeStr) + 1

        progStr = RC.MINES_REMAINING.text() % self.progressString()
        self._win.addstr(0, cWidth - len(progStr) - 1, progStr, RC.MINES_REMAINING.attr())

    def drawButtons(self):
        cStart = 0

        for btn in self._buttons.values():
            self._win.addstr(0, cStart, btn.text(), btn.attr())
            cStart += 1 + len(btn.text())

    def retrieveClickedButton(self, cX, cY):
        if cY != curses.LINES - 1:
            return None

        cStart = 0
        for k, btn in self._buttons.items():

            if cX >= cStart and cX < cStart + len(btn.text()):
                return k
            cStart += 1 + len(btn.text())

        return None

    def updateClock(self):
        self.drawStatus(clockOnly=True)
        self._win.noutrefresh()

    def updateAll(self):
        self.drawButtons()
        self.drawStatus()
        self._win.noutrefresh()

class LogWindow:

    def __init__(self, width):

        self._win = curses.newwin(curses.LINES, width, 0, curses.COLS - width)
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

    def updateAll(self):

        self.printLog()
        self._win.border()
        self._win.noutrefresh()

    def _maxLines(self):
        cHeight, _ = self._win.getmaxyx()
        return cHeight - RC.LOG_BORDER_CHEIGHT * 2

class EventLoop:

    def mineFieldOnMouseClick(self, mX, mY, btn):

        coor = MINE_FIELD_WINDOW.retrieveMineFieldCoordinate(mX, mY)

        if coor is None:
            return

        if btn == curses.BUTTON1_PRESSED:

            if STATUS_WINDOW.isTimerReset():
                STATUS_WINDOW.startTimer()

            x, y = coor
            LOG_WINDOW.push("poke %d %d" % (x, y))
            SHELL.run("poke %d %d" % (x, y))
            for line in SHELL.getOutput():
                LOG_WINDOW.push(line)

            if MINE_FIELD_WINDOW.isBoomed() or MINE_FIELD_WINDOW.isFinished():
                STATUS_WINDOW.stopTimer()

        elif btn == curses.BUTTON3_PRESSED:
            x, y = coor
            LOG_WINDOW.push("toggle %d %d" % (x, y))
            SHELL.run("toggle %d %d" % (x, y))
            for line in SHELL.getOutput():
                LOG_WINDOW.push(line)
        else:
            pass

    def statusBarOnMouseClick(self, mX, mY):

        button = STATUS_WINDOW.retrieveClickedButton(mX, mY)
        if button == StatusWindow.BUTTON_NEW_GAME:
            self.newGameButtonOnMouseClick()
        elif button == StatusWindow.BUTTON_PAUSE:
            self.pauseGameButtonOnMouseClick()
        elif button == StatusWindow.BUTTON_RECORDS:
            self.bestRecordButtonOnMouseClick()
        else: pass

    def newGameButtonOnMouseClick(self):
        LOG_WINDOW.push("OMG")
        RestartGame()

    def pauseGameButtonOnMouseClick(self):
        pass

    def bestRecordButtonOnMouseClick(self):
        pass

    def run(self):

        while True:

            event = ROOT_SCREEN.getch()

            if event == curses.KEY_MOUSE:
                mouseEvent = curses.getmouse()
                _, mX, mY, _, btn = mouseEvent

                self.mineFieldOnMouseClick(mX, mY, btn)
                self.statusBarOnMouseClick(mX, mY)

                refreshAll()

def refreshAll():

    MINE_FIELD_WINDOW.updateAll()
    STATUS_WINDOW.updateAll()
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

def RestartGame():

    mfWidthMax, mfHeightMax = MINE_FIELD_WINDOW.getMaxMineFieldSize()
    if mfWidthMax >= RC.MINE_FIELD_WIDTH and mfHeightMax >= RC.MINE_FIELD_HEIGHT:
        shellCmd = "minefield %d %d %d" % (RC.MINE_FIELD_WIDTH, RC.MINE_FIELD_HEIGHT, RC.MINE_FIELD_MINES)
    else:
        shellCmd = "minefield %d %d %d" % (mfWidthMax, mfHeightMax, int(mfWidthMax * mfHeightMax * RC.MINE_FIELD_DEFAULT_MINES_PERCENTAGE))
    SHELL.run(shellCmd)
    STATUS_WINDOW.resetTimer()

class ClockUpdater(threading.Thread):

    def run(self):
        while True:
            STATUS_WINDOW.updateClock()
            curses.doupdate()
            time.sleep(0.1)

def Main(stdscr):

    global MINE_FIELD_WINDOW
    global STATUS_WINDOW
    global LOG_WINDOW
    global ROOT_SCREEN
    global SHELL

    InitCurses()
    stdscr.clear()

    SHELL = Shell.Shell()
    ROOT_SCREEN = stdscr
    MINE_FIELD_WINDOW = MineFieldWindow(curses.COLS - RC.LOG_WINDOW_WIDTH)
    STATUS_WINDOW = StatusWindow(curses.COLS - RC.LOG_WINDOW_WIDTH)
    LOG_WINDOW = LogWindow(RC.LOG_WINDOW_WIDTH)

    RestartGame()

    clockUpdater = ClockUpdater()
    clockUpdater.daemon = True
    clockUpdater.start()

    stdscr.refresh()
    refreshAll()
    EventLoop().run()

curses.wrapper(Main)
