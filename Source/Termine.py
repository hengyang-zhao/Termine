#!/usr/bin/env python3

import curses
import datetime
import pickle
import threading
import time
import sys

from collections import deque
from collections import OrderedDict

import RC
import Shell

MINE_FIELD_WINDOW = None
STATUS_WINDOW = None
RECORD_WINDOW = None
LOG_WINDOW = None
TIMER = None
SHELL = None
ROOT_SCREEN = None

class MineFieldWindow:

    def __init__(self, width):

        self._win = curses.newwin(curses.LINES - 3, width, 0, 0)

    def getMaxMineFieldSize(self):

        cHeight, cWidth = self._win.getmaxyx()
        mfWidth = (cWidth - (RC.MINE_FIELD_MARGIN_CWIDTH + RC.MINE_FIELD_BORDER_CWIDTH) * 2 - 1) // (RC.MINE_FIELD_CELL_CWIDTH + 1)
        mfHeight = (cHeight - (RC.MINE_FIELD_MARGIN_CHEIGHT + RC.MINE_FIELD_BORDER_CHEIGHT) * 2 - 1) // (RC.MINE_FIELD_CELL_CHEIGHT + 1)

        return mfWidth, mfHeight

    def drawBorder(self):
        self._win.border()

        mfWidth, mfHeight = self.currentMineFieldSize()
        title = " Termine Field %d x %d " % (mfWidth, mfHeight)

        cX = 2
        self._win.addch(0, cX, curses.ACS_RTEE)
        cX += 1
        self._win.addstr(0, cX, title)
        cX += len(title)
        self._win.addch(0, cX, curses.ACS_LTEE)

    def updateAll(self):

        self._win.erase()
        self.drawBorder()
        self.drawMineField()
        self._win.noutrefresh()

    def retrieveMineFieldCoordinate(self, cX, cY):

        xCStart, yCStart = self._mineFieldXYCStart()
        xCEnd, yCEnd = self._mineFieldYXCEnd()

        if cX < xCStart or cY < yCStart or cX >= xCEnd or cY >= yCEnd or (cX - xCStart) % (RC.MINE_FIELD_CELL_CWIDTH + 1) == 0 or (cY - yCStart) % (RC.MINE_FIELD_CELL_CHEIGHT + 1) == 0:
            return None

        return (cX - xCStart) // 4, (cY - yCStart) // 2

    def drawMineField(self):

        mfWidth, mfHeight = self.currentMineFieldSize()

        for mfX in range(mfWidth):
            for mfY in range(mfHeight):
                self.drawMineCell(mfX, mfY)

    def drawMineCell(self, mfX, mfY):

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


        if TIMER.isPaused() and not self.isBoomed() and not self.isFinished():
            cell = RC.CELL_PAUSED
        else:
            cell = self.cellAt(mfX, mfY)

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
    BUTTON_LEAVE = 3

    def __init__(self, width):
        self._win = curses.newwin(3, width, curses.LINES - 3, 0)

    def _buttons(self):
        if TIMER.isPaused() and not MINE_FIELD_WINDOW.isFinished() and not MINE_FIELD_WINDOW.isBoomed():
            return OrderedDict({
                StatusWindow.BUTTON_NEW_GAME: RC.BUTTON_NEW_GAME,
                StatusWindow.BUTTON_PAUSE: RC.BUTTON_RESUME,
                StatusWindow.BUTTON_RECORDS: RC.BUTTON_RECORDS,
                StatusWindow.BUTTON_LEAVE: RC.BUTTON_LEAVE
                })
        else:
            return OrderedDict({
                StatusWindow.BUTTON_NEW_GAME: RC.BUTTON_NEW_GAME,
                StatusWindow.BUTTON_PAUSE: RC.BUTTON_PAUSE,
                StatusWindow.BUTTON_RECORDS: RC.BUTTON_RECORDS,
                StatusWindow.BUTTON_LEAVE: RC.BUTTON_LEAVE
                })

    def clockString(self):
        elapsed = TIMER.elapsed()

        nMins = elapsed.seconds // 60
        nSecs = elapsed.seconds % 60
        nTenths = elapsed.microseconds // 100000

        if (nMins > 99):
            nMins = 99
            nSecs = 99
            nTenths = 9

        return "%02d:%02d.%01d" % (nMins, nSecs, nTenths)

    def progressString(self):
        SHELL.run("query flags")
        nFlags = int(next(SHELL.getOutput()))
        SHELL.run("query mines")
        nMines = int(next(SHELL.getOutput()))

        return "%d flags / %d mines" % (nFlags, nMines)

    def drawStatus(self, clockOnly=False):
        _, cWidth = self._win.getmaxyx()

        timeStr = RC.TIMER.text() % self.clockString()
        self._win.addstr(1, cWidth - len(timeStr) - 1, timeStr, RC.TIMER.attr())

        if clockOnly is True: return

        cWidth -= len(timeStr) + 1

        progStr = RC.MINES_REMAINING.text() % self.progressString()
        self._win.addstr(1, cWidth - len(progStr) - 1, progStr, RC.MINES_REMAINING.attr())

        cWidth -= len(progStr) + 2
        return cWidth

    def drawButtons(self):
        cStart = 1

        for btn in self._buttons().values():
            self._win.addstr(1, cStart, btn.text(), btn.attr())
            cStart += 1 + len(btn.text())

        return cStart

    def drawProgressBar(self, progBarCBegin, progBarCEnd):
        self._win.addstr(1, progBarCBegin, "[")
        self._win.addstr(1, progBarCEnd - 1, "] ")
        progBarLength = progBarCEnd - progBarCBegin - 2

        mfWidth, mfHeight = MINE_FIELD_WINDOW.currentMineFieldSize()
        nCells = mfWidth * mfHeight

        SHELL.run("query mines")
        nMines = int(next(SHELL.getOutput()))

        SHELL.run("query revealed")
        nRevealed = len(list(SHELL.getOutput()))

        nNonMines = nCells - nMines

        nSharps = progBarLength * nRevealed // nNonMines
        nDashes = progBarLength - nSharps

        percent = str(nRevealed * 100 // nNonMines) + "%"

        self._win.addstr(1, progBarCBegin + 1, "#" * nSharps)
        self._win.addstr(1, progBarCBegin + 1 + nSharps, "-" * nDashes)

        self._win.addstr(1, progBarCEnd - 1 - len(percent), percent)

    def retrieveClickedButton(self, cX, cY):
        if cY != curses.LINES - 2:
            return None

        cStart = 1
        for k, btn in self._buttons().items():

            if cX >= cStart and cX < cStart + len(btn.text()):
                return k
            cStart += 1 + len(btn.text())

        return None

    def updateClock(self):
        self.drawStatus(clockOnly=True)
        self._win.border()
        self._win.noutrefresh()

    def updateAll(self):
        progBarCBegin = self.drawButtons()
        progBarCEnd = self.drawStatus()
        self.drawProgressBar(progBarCBegin, progBarCEnd)
        self._win.noutrefresh()

class LogWindow:

    def __init__(self, width):

        self._win = curses.newwin(curses.LINES - 3, width, 0, curses.COLS - width)
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

    def drawBorder(self):
        self._win.border()
        title = " Log "

        cX = 2
        self._win.addch(0, cX, curses.ACS_RTEE)
        cX += 1
        self._win.addstr(0, cX, title)
        cX += len(title)
        self._win.addch(0, cX, curses.ACS_LTEE)

    def updateAll(self):

        self.printLog()
        self.drawBorder()
        self._win.noutrefresh()

    def _maxLines(self):
        cHeight, _ = self._win.getmaxyx()
        return cHeight - RC.LOG_BORDER_CHEIGHT * 2

class RecordItem:

    def __init__(self, duration, whenCreated):
        self.duration = duration
        self.whenCreated = whenCreated

    def __str__(self):
        nMins = self.duration.seconds // 60
        nSecs = self.duration.seconds % 60
        nTenths = self.duration.microseconds // 100000

        return "%d:%02d.%01d sec (%s)" % (nMins, nSecs, nTenths,
                self.whenCreated.strftime("%Y/%m/%d %H:%M:%S"))

class RecordWindow:
    def __init__(self):

        xCStart = (curses.COLS - RC.RECORD_WINDOW_CWIDTH) // 2
        yCStart = (curses.LINES - RC.RECORD_WINDOW_CHEIGHT) // 2
        self._win = curses.newwin(RC.RECORD_WINDOW_CHEIGHT, RC.RECORD_WINDOW_CWIDTH, yCStart, xCStart)
        self._backWin = curses.newwin(RC.RECORD_WINDOW_CHEIGHT + 2, RC.RECORD_WINDOW_CWIDTH + 2, yCStart - 1, xCStart - 1)
        self._records = {}
        self._currentRecord = None
        self.loadRecords()

        self.visible = False

    def updateRecord(self):
        self.flushRecords()
        self._currentRecord = RecordItem(TIMER.elapsed(), datetime.datetime.now())

    def recordCategoryString(self):

        SHELL.run("query mines")
        nMines = next(SHELL.getOutput())

        SHELL.run("query width")
        mfWidth = next(SHELL.getOutput())

        SHELL.run("query height")
        mfHeight = next(SHELL.getOutput())

        return "%s mines on %s by %s field" % (nMines, mfWidth, mfHeight)

    def loadRecords(self):
        try:
            with open(RC.RECORD_FILE_PATH, 'rb') as recFile:
                self._records = pickle.load(recFile)
        except:
            self._records = {}

    def flushRecords(self):
        if self._currentRecord is None:
            return

        self._records.setdefault(self.recordCategoryString(), []).append(self._currentRecord)
        self._currentRecord = None
        with open(RC.RECORD_FILE_PATH, 'wb') as recFile:
            pickle.dump(self._records, recFile)

    def drawRecords(self):
        cX, cY = 1, 1
        _, cHeight = self._win.getmaxyx()
        rankMax = cHeight - 2
        rank = 1

        dispTable = []
        for rec in self._records.get(self.recordCategoryString(), []):
            dispTable.append((rec, False))

        if self._currentRecord is not None:
            dispTable.append((self._currentRecord, True))

        for rec, isCurrent in sorted(dispTable, key=lambda r: r[0].duration):
            self._win.addstr(cY, cX, "%2d: %s" % (rank, str(rec)),
                    RC.RECORD_CURRENT_STYLE.attr() if isCurrent is True else RC.RECORD_DEFAULT_STYLE.attr())

            cY += 1
            rank += 1

    def drawBorder(self):
        self._win.border()
        title = " Best records (%s) " % self.recordCategoryString()
        cX = 2
        self._win.addch(0, cX, curses.ACS_RTEE)
        cX += 1
        self._win.addstr(0, cX, title)
        cX += len(title)
        self._win.addch(0, cX, curses.ACS_LTEE)

    def updateAll(self):
        if self.visible is False:
            return

        self._backWin.erase()
        self.drawBorder()
        self.drawRecords()
        self._backWin.noutrefresh()
        self._win.noutrefresh()

class Timer:
    def __init__(self):
        self._whenStarted = None
        self._whenPaused = None

    def start(self):
        assert self.isReset() is True
        self._whenStarted = datetime.datetime.now()

    def pause(self):
        assert self.isRunning() is True
        self._whenPaused = datetime.datetime.now()

    def resume(self):
        assert self.isPaused() is True
        self._whenStarted = datetime.datetime.now() - self.elapsed()
        self._whenPaused = None

    def reset(self):
        self._whenStarted = None
        self._whenPaused = None

    def elapsed(self):
        if self.isReset():
            return datetime.timedelta(0)
        elif self.isPaused():
            return self._whenPaused - self._whenStarted
        else:
            assert self.isRunning()
            return datetime.datetime.now() - self._whenStarted

    def isRunning(self):
        return self._whenStarted is not None and self._whenPaused is None

    def isReset(self):
        return self._whenStarted is None and self._whenPaused is None

    def isPaused(self):
        return self._whenStarted is not None and self._whenPaused is not None

class EventLoop:

    def mineFieldOnMouseClick(self, mX, mY, btn):

        if TIMER.isPaused():
            return False

        coor = MINE_FIELD_WINDOW.retrieveMineFieldCoordinate(mX, mY)

        if coor is None:
            return False

        if btn == curses.BUTTON1_PRESSED:

            if TIMER.isReset():
                TIMER.start()

            x, y = coor
            LOG_WINDOW.push("poke %d %d" % (x, y))
            SHELL.run("poke %d %d" % (x, y))
            for line in SHELL.getOutput():
                LOG_WINDOW.push(line)

            if MINE_FIELD_WINDOW.isBoomed() or MINE_FIELD_WINDOW.isFinished():
                TIMER.pause()

            if MINE_FIELD_WINDOW.isFinished():
                RECORD_WINDOW.updateRecord()
                self.bestRecordButtonOnMouseClick()

        elif btn == curses.BUTTON3_PRESSED:
            x, y = coor
            LOG_WINDOW.push("toggle %d %d" % (x, y))
            SHELL.run("toggle %d %d" % (x, y))
            for line in SHELL.getOutput():
                LOG_WINDOW.push(line)
        else:
            pass

        return True

    def statusBarOnMouseClick(self, mX, mY):

        button = STATUS_WINDOW.retrieveClickedButton(mX, mY)

        if RECORD_WINDOW.visible is True:
            self.bestRecordButtonOnMouseClick()
            return True

        if button == StatusWindow.BUTTON_NEW_GAME:
            self.newGameButtonOnMouseClick()
            return True

        if button == StatusWindow.BUTTON_PAUSE:
            self.pauseGameButtonOnMouseClick()
            return True

        if button == StatusWindow.BUTTON_RECORDS:
            self.bestRecordButtonOnMouseClick()
            return True

        if button == StatusWindow.BUTTON_LEAVE:
            self.leaveButtonOnMouseClick()
            return True

        return False

    def newGameButtonOnMouseClick(self):
        if RECORD_WINDOW.visible is True:
            return

        RestartGame()

    def pauseGameButtonOnMouseClick(self):
        if RECORD_WINDOW.visible is True or TIMER.isReset() is True:
            return

        if TIMER.isPaused() is True:
            if not MINE_FIELD_WINDOW.isBoomed() and not MINE_FIELD_WINDOW.isFinished():
                TIMER.resume()
            return

        if TIMER.isRunning() is True:
            TIMER.pause()

    def bestRecordButtonOnMouseClick(self):

        if RECORD_WINDOW.visible is True:

            RECORD_WINDOW.visible = False

            if TIMER.isReset() is True:
                return

            if TIMER.isPaused() is True:
                if not MINE_FIELD_WINDOW.isBoomed() and not MINE_FIELD_WINDOW.isFinished():
                    TIMER.resume()
                return

        else:

            RECORD_WINDOW.visible = True

            if TIMER.isRunning() is True:
                TIMER.pause()

    def leaveButtonOnMouseClick(self):
        RECORD_WINDOW.flushRecords()
        sys.exit(0) 

    def run(self):

        while True:

            try:
                event = ROOT_SCREEN.getch()
            except KeyboardInterrupt:
                continue

            if event == curses.KEY_MOUSE:
                try:
                    mouseEvent = curses.getmouse()
                except:
                    continue
                _, mX, mY, _, btn = mouseEvent

                if self.statusBarOnMouseClick(mX, mY) is True:

                    refreshAll()
                    continue

                if self.mineFieldOnMouseClick(mX, mY, btn) is True:

                    refreshAll()
                    continue

def refreshAll():

    MINE_FIELD_WINDOW.updateAll()
    STATUS_WINDOW.updateAll()
    LOG_WINDOW.updateAll()
    RECORD_WINDOW.updateAll()
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
    RECORD_WINDOW.flushRecords()
    TIMER.reset()

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
    global RECORD_WINDOW
    global TIMER
    global SHELL

    InitCurses()
    stdscr.clear()

    SHELL = Shell.Shell()
    ROOT_SCREEN = stdscr
    MINE_FIELD_WINDOW = MineFieldWindow(curses.COLS - RC.LOG_WINDOW_CWIDTH)
    STATUS_WINDOW = StatusWindow(curses.COLS)
    LOG_WINDOW = LogWindow(RC.LOG_WINDOW_CWIDTH)
    RECORD_WINDOW = RecordWindow()
    TIMER = Timer()

    RestartGame()

    clockUpdater = ClockUpdater()
    clockUpdater.daemon = True
    clockUpdater.start()

    stdscr.refresh()
    refreshAll()
    EventLoop().run()

curses.wrapper(Main)
