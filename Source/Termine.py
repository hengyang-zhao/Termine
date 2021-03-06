#!/usr/bin/env python3

import argparse
import curses
import datetime
import pickle
import threading
import time
import sys
import re

from collections import deque
from collections import OrderedDict

import Styles
import Shell

MINE_FIELD_WINDOW = None
STATUS_WINDOW = None
RECORD_WINDOW = None
LOG_WINDOW = None
TIMER = None
SHELL = None
ROOT_SCREEN = None
ARGUMENTS = None
RC = None

class MineFieldWindow:

    def __init__(self):

        self._cursorX = 0
        self._cursorY = 0

        self._isCursorVisible = False

        self.resize()

    def toggleCursorVisible(self):
        self._isCursorVisible = not self._isCursorVisible

    def isCursorVisible(self):
        return self._isCursorVisible is True

    def getCursor(self):
        if self._isCursorVisible is True:
            return self._cursorX, self._cursorY

        else:
            return None

    def translateCursor(self, dx, dy):
        newX = self._cursorX + dx
        newY = self._cursorY + dy

        xMax, yMax = self.currentMineFieldSize()
        if newX < 0 or newX >= xMax or newY < 0 or newY >= yMax:
            if RC.MINE_FIELD_ALLOW_CURSOR_WRAP is False:
                return

        self._cursorX, self._cursorY = newX % xMax, newY % yMax

    def resize(self):

        rootCWidth, rootCHeight = GameControl.safeTerminalSize()
        self._win = curses.newwin(rootCHeight - 3, rootCWidth - RC.LOG_WINDOW_CWIDTH, 0, 0)

    def getMaxMineFieldSize(self):

        cHeight, cWidth = self._win.getmaxyx()
        mfWidth = (cWidth - (RC.MINE_FIELD_MARGIN_CWIDTH + RC.MINE_FIELD_BORDER_CWIDTH) * 2 - 1) // (RC.MINE_FIELD_CELL_CWIDTH + 1)
        mfHeight = (cHeight - (RC.MINE_FIELD_MARGIN_CHEIGHT + RC.MINE_FIELD_BORDER_CHEIGHT) * 2 - 1) // (RC.MINE_FIELD_CELL_CHEIGHT + 1)

        return mfWidth, mfHeight

    def isAbleToDrawMineField(self):
        mfWidthMax, mfHeightMax = self.getMaxMineFieldSize()
        mfWidth, mfHeight = self.currentMineFieldSize()

        return mfWidth <= mfWidthMax and mfHeight <= mfHeightMax

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

    def drawTooSmallMineField(self):

        msgLength = len(RC.MINE_FIELD_TOO_SMALL_MESSAGE.text())

        cHeight, cWidth = self._win.getmaxyx()

        self._win.addstr(cHeight // 2, (cWidth - msgLength) // 2,
                RC.MINE_FIELD_TOO_SMALL_MESSAGE.text(),
                RC.MINE_FIELD_TOO_SMALL_MESSAGE.attr())

    def updateAll(self):

        self._win.erase()

        if self.isAbleToDrawMineField() is True:
            self.drawMineField()
        else:
            self.drawTooSmallMineField()

        self.drawBorder()

        self._win.noutrefresh()

    def retrieveMineFieldCoordinate(self, cX, cY):

        if self.isAbleToDrawMineField() is False:
            return None

        xCStart, yCStart = self._mineFieldXYCStart()
        xCEnd, yCEnd = self._mineFieldYXCEnd()

        if cX < xCStart or cY < yCStart or cX >= xCEnd or cY >= yCEnd or (cX - xCStart) % (RC.MINE_FIELD_CELL_CWIDTH + 1) == 0 or (cY - yCStart) % (RC.MINE_FIELD_CELL_CHEIGHT + 1) == 0:
            return None

        return (cX - xCStart) // (1 + RC.MINE_FIELD_CELL_CWIDTH), (cY - yCStart) // (1 + RC.MINE_FIELD_CELL_CHEIGHT)

    def drawMineField(self):

        mfWidth, mfHeight = self.currentMineFieldSize()

        for mfX in range(mfWidth):
            for mfY in range(mfHeight):
                if mfX == self._cursorX and mfY == self._cursorY:
                    continue
                self.drawMineCell(mfX, mfY)

        self.drawMineCell(self._cursorX, self._cursorY)

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
        elif self._isCursorVisible is True and mfX == self._cursorX and mfY == self._cursorY:
            borderStyle = RC.MINE_FIELD_BORDER_FOCUSED_STYLE.attr()
            ulCorner = curses.ACS_ULCORNER
            urCorner = curses.ACS_URCORNER
            llCorner = curses.ACS_LLCORNER
            lrCorner = curses.ACS_LRCORNER
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

        for i in range(RC.MINE_FIELD_CELL_CHEIGHT):

            self._win.addstr(yCStart + mfY * (RC.MINE_FIELD_CELL_CHEIGHT + 1) + 1 + i,
                    xCStart + mfX * (RC.MINE_FIELD_CELL_CWIDTH + 1) + 1,
                    cell.text() if i == RC.MINE_FIELD_CELL_CHEIGHT // 2 else cell.padding(),
                    cell.attr())


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

    def __init__(self):

        self.resize()

    def resize(self):
        rootCWidth, rootCHeight = GameControl.safeTerminalSize()
        self._win = curses.newwin(3, rootCWidth, rootCHeight - 3, 0)

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
        SHELL.run("query flagscount")
        nFlags = int(next(SHELL.getOutput()))
        SHELL.run("query minescount")
        nMines = int(next(SHELL.getOutput()))

        return "%d flags / %d mines" % (nFlags, nMines)

    def drawStatus(self, clockOnly=False):
        _, cWidth = self._win.getmaxyx()

        timeStr = RC.STATUS_TIMER.text() % self.clockString()
        self._win.addstr(1, cWidth - len(timeStr) - 1, timeStr, RC.STATUS_TIMER.attr())

        if clockOnly is True: return

        cWidth -= len(timeStr) + 1

        progStr = RC.STATUS_MINE_REMAINING.text() % self.progressString()
        self._win.addstr(1, cWidth - len(progStr) - 1, progStr, RC.STATUS_MINE_REMAINING.attr())

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

        SHELL.run("query minescount")
        nMines = int(next(SHELL.getOutput()))

        SHELL.run("query revealedcount")
        nRevealed = int(next(SHELL.getOutput()))

        nNonMines = nCells - nMines

        nSharps = progBarLength * nRevealed // nNonMines
        nDashes = progBarLength - nSharps

        percent = str(nRevealed * 100 // nNonMines) + "%"

        self._win.addstr(1, progBarCBegin + 1, "#" * nSharps)
        self._win.addstr(1, progBarCBegin + 1 + nSharps, "-" * nDashes)

        self._win.addstr(1, progBarCEnd - 1 - len(percent), percent)

    def retrieveClickedButton(self, cX, cY):

        _, rootCHeight = GameControl.safeTerminalSize()

        if cY != rootCHeight - 2:
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

    def __init__(self):

        self.resize()
        self._logLines = deque()

    def resize(self):

        rootCWidth, rootCHeight = GameControl.safeTerminalSize()
        self._win = curses.newwin(rootCHeight - 3, RC.LOG_WINDOW_CWIDTH, 0, rootCWidth - RC.LOG_WINDOW_CWIDTH)

    def push(self, s):

        self._logLines.append(s)

    def printLog(self):

        self._win.erase()

        while len(self._logLines) > self._maxLines():
            self._logLines.popleft()

        maxLength = RC.LOG_WINDOW_CWIDTH - RC.LOG_BORDER_CWIDTH * 2

        y, x = self._win.getyx()
        for line in self._logLines:
            self._win.addstr(y + 1, x + 1, line[:maxLength])
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

        self._records = {}
        self._currentRecord = None
        self.loadRecords()

        self.resize()

        self.visible = False

    def resize(self):
        rootCWidth, rootCHeight = GameControl.safeTerminalSize()

        xCStart = (rootCWidth - RC.RECORD_WINDOW_CWIDTH) // 2
        yCStart = (rootCHeight - RC.RECORD_WINDOW_CHEIGHT) // 2

        self._win = curses.newwin(RC.RECORD_WINDOW_CHEIGHT, RC.RECORD_WINDOW_CWIDTH, yCStart, xCStart)
        self._backWin = curses.newwin(RC.RECORD_WINDOW_CHEIGHT + 2, RC.RECORD_WINDOW_CWIDTH + 2, yCStart - 1, xCStart - 1)

    def updateRecord(self):
        self.flushRecords()
        self._currentRecord = RecordItem(TIMER.elapsed(), datetime.datetime.now())

    def recordCategoryString(self):

        SHELL.run("query minescount")
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
        cHeight, _ = self._win.getmaxyx()
        rankMax = cHeight - 2
        rank = 1

        dispTable = []
        for rec in self._records.get(self.recordCategoryString(), []):
            dispTable.append((rec, False))

        if self._currentRecord is not None:
            dispTable.append((self._currentRecord, True))

        for rec, isCurrent in sorted(dispTable, key=lambda r: r[0].duration):

            if rank > rankMax:
                break

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

class Arguments:

    STANDARD_EASY = 0
    STANDARD_MEDIUM = 1
    STANDARD_HARD = 2

    class MineFieldCellCSize:
        def __init__(self, sizeString):

            m = re.match(r'(\d+)x(\d+)', sizeString)
            if m is None:
                raise argparse.ArgumentTypeError("Should be in format WxH (example: 5x3)")
            self._width = int(m.group(1))
            self._height = int(m.group(2))

            self._checkValues()

        def _checkValues(self):
            if self._width < 1 or self._height < 1:
                raise argparse.ArgumentTypeError("MineField cell size should be at least 1x1")

        def __repr__(self):
            return "%dx%d" % (self._width, self._height)

        def value(self):
            return self._width, self._height

    class MineFieldSize:
        def __init__(self, sizeString):

            if sizeString == 'fullscreen':
                self.isFullScreen = True
                return

            m = re.match(r'(\d+)x(\d+)', sizeString)
            if m is None:
                raise argparse.ArgumentTypeError("Should be in format WxH (example: 10x8) or 'fullscreen'")
            self._width = int(m.group(1))
            self._height = int(m.group(2))
            self.isFullScreen = False

            self._checkValues()

        def _checkValues(self):
            if self._width < 4 or self._height < 4:
                raise argparse.ArgumentTypeError("MineField size should be at least 4x4")

        def __repr__(self):
            if self.isFullScreen is True:
                return "fullscreen"
            else:
                return "%dx%d" % (self._width, self._height)

        def value(self):
            if self.isFullScreen is True:
                return None
            else:
                return self._width, self._height

    class MineDensity:
        def __init__(self, percentString):
            
            m = re.match(r'(\d+)%', percentString)
            if m is None:
                raise argparse.ArgumentTypeError("Should be in format N% (example: 10%)")
            self._percent = int(m.group(1))
            self._checkValues()

        def _checkValues(self):
            if self._percent < 0 or self._percent > 100:
                raise argparse.ArgumentTypeError("Mine density should be in range 0% ~ 100%")

        def __repr__(self):
            return "%d%%" % (self._percent)

        def value(self):
            return self._percent / 100

    def __init__(self):
        self._parser = argparse.ArgumentParser(description='Termine - A Terminal Based Mine Sweeping Game')

        self._parser.add_argument("-S", "--standard", choices=['easy', 'medium', 'hard'], help="standard minefield configurations (easy: 8x8, 10 mines, medium 16x16, 40 mines, hard 30x16, 99 mines)")
        self._parser.add_argument("-s", "--size", type=Arguments.MineFieldSize, default='fullscreen', help="minefield size in format WIDTHxHEIGHT")
        self._parser.add_argument("-t", "--cell-size", type=Arguments.MineFieldCellCSize, default='5x3', help="mine cell size (in characters) in format WIDTHxHEIGHT")
        self._parser.add_argument("-d", "--density", type=Arguments.MineDensity, default='15%', help="mines density in format PERCENT%%")
        self._parser.add_argument("-R", "--dump-record", action='store_true')

        self._parser.add_argument('-v', '--version', action='version', version='%(prog)s 0.2')

    def fullScreenMineFieldRequested(self):
        return self._cookedArgs.size.isFullScreen

    def standardDifficulty(self):
        return {
                'easy': Arguments.STANDARD_EASY,
                'medium': Arguments.STANDARD_MEDIUM,
                'hard': Arguments.STANDARD_HARD
        }.get(self._cookedArgs.standard, None)

    def mineFieldSize(self):
        return self._cookedArgs.size.value()

    def mineFieldCellCSize(self):
        return self._cookedArgs.cell_size.value()

    def minesDensity(self):
        return self._cookedArgs.density.value()

    def needsListingRecord(self):
        return self._cookedArgs.dump_record

    def parse(self):
        self._cookedArgs = self._parser.parse_args()

class GameControl:

    @staticmethod
    def initArguments():

        global ARGUMENTS

        ARGUMENTS = Arguments()
        ARGUMENTS.parse()

    @staticmethod
    def initRC():

        global RC

        mfCellCWdith, mfCellCHeight = ARGUMENTS.mineFieldCellCSize()

        RC = Styles.RCProvider(
                mineFieldCellCWidth=mfCellCWdith,
                mineFieldCellCHeight=mfCellCHeight
                )

    @staticmethod
    def initGame():

        global MINE_FIELD_WINDOW
        global STATUS_WINDOW
        global LOG_WINDOW
        global RECORD_WINDOW
        global TIMER
        global SHELL

        SHELL = Shell.Shell()
        TIMER = Timer()
        STATUS_WINDOW = StatusWindow()
        LOG_WINDOW = LogWindow()
        RECORD_WINDOW = RecordWindow()
        MINE_FIELD_WINDOW = MineFieldWindow()

    @staticmethod
    def dumpRecord():

        try:
            with open(RC.RECORD_FILE_PATH, 'rb') as recFile:
                recordBook = pickle.load(recFile)
        except Exception as e:
            recordBook = {}

        for title, records in recordBook.items():
            print("<><><> %s <><><>" % title)
            
            rank = 1
            for rec in sorted(records, key=lambda r: r.duration):
                print("%4d: %s" % (rank, rec))
                rank += 1

            print()

    @staticmethod
    def terminalSize():
        if ROOT_SCREEN is None:
            return curses.COLS, curses.LINES
        else:
            rootCHeight, rootCWidth = ROOT_SCREEN.getmaxyx()
            return rootCWidth, rootCHeight

    @staticmethod
    def safeTerminalSize():
        rootCWidth, rootCHeight = GameControl.terminalSize()
        if rootCWidth < RC.TERM_CWIDTH_LIMIT:
            rootCWidth = RC.TERM_CWIDTH_LIMIT

        if rootCHeight < RC.TERM_CHEIGHT_LIMIT:
            rootCHeight = RC.TERM_CHEIGHT_LIMIT

        return rootCWidth, rootCHeight

    @staticmethod
    def initDisplay(screen):

        global ROOT_SCREEN

        ROOT_SCREEN = screen

        rootCWidth, rootCHeight = GameControl.terminalSize()
        if rootCHeight < RC.TERM_CHEIGHT_LIMIT or rootCWidth < RC.TERM_CWIDTH_LIMIT:
            GameControl.abortWithMessage("Terminal size %d by %d is too small. (Should be at least %d by %d)" % (
                rootCWidth, rootCHeight, RC.TERM_CWIDTH_LIMIT, RC.TERM_CHEIGHT_LIMIT))

        if (curses.has_colors()):
            curses.start_color()
            curses.use_default_colors()

            curses.init_pair(0, curses.COLOR_BLACK, -1)
            curses.init_pair(1, curses.COLOR_RED, -1)
            curses.init_pair(2, curses.COLOR_GREEN, -1)
            curses.init_pair(3, curses.COLOR_YELLOW, -1)
            curses.init_pair(4, curses.COLOR_BLUE, -1)
            curses.init_pair(5, curses.COLOR_MAGENTA, -1)
            curses.init_pair(6, curses.COLOR_CYAN, -1)
            curses.init_pair(7, curses.COLOR_WHITE, -1)

        curses.mousemask(curses.BUTTON1_PRESSED | curses.BUTTON3_PRESSED)
        curses.mouseinterval(0)
        curses.curs_set(False)

        ROOT_SCREEN.clear()

    @staticmethod
    def pauseGame():
        if TIMER.isReset() is True:
            return

        if TIMER.isRunning() is True:
            TIMER.pause()

    @staticmethod
    def unpauseGame():
        if TIMER.isReset() is True:
            return

        if MINE_FIELD_WINDOW.isAbleToDrawMineField() is False:
            return

        if TIMER.isPaused() is True:
            if not MINE_FIELD_WINDOW.isBoomed() and not MINE_FIELD_WINDOW.isFinished():
                TIMER.resume()
            return

    @staticmethod
    def togglePauseGame():

        if TIMER.isRunning() is True:
            GameControl.pauseGame()
        else:
            GameControl.unpauseGame()

    @staticmethod
    def restartGame():

        mfWidthMax, mfHeightMax = MINE_FIELD_WINDOW.getMaxMineFieldSize()

        if ARGUMENTS.standardDifficulty() == Arguments.STANDARD_EASY:
            mfWidth, mfHeight, nMines = 8, 8, 10

        elif ARGUMENTS.standardDifficulty() == Arguments.STANDARD_MEDIUM:
            mfWidth, mfHeight, nMines = 16, 16, 40

        elif ARGUMENTS.standardDifficulty() == Arguments.STANDARD_HARD:
            mfWidth, mfHeight, nMines = 30, 16, 99

        elif ARGUMENTS.fullScreenMineFieldRequested():
            mfWidth, mfHeight = mfWidthMax, mfHeightMax
            nMines = round(mfWidth * mfHeight * ARGUMENTS.minesDensity())

        else:
            mfWidth, mfHeight = ARGUMENTS.mineFieldSize()
            nMines = round(mfWidth * mfHeight * ARGUMENTS.minesDensity())

        nMinesMax = mfWidth * mfHeight - 9

        if mfWidth > mfWidthMax or mfHeight > mfHeightMax:
            GameControl.abortWithMessage("Unable to create %d by %d minefield. The current maximum is %d by %d." % (mfWidth, mfHeight, mfWidthMax, mfHeightMax))

        if nMines > nMinesMax:
            GameControl.abortWithMessage("Unable to deploy %d mines (density %g%%) on %d by %d minefield." % (nMines, ARGUMENTS.minesDensity() * 100, mfWidth, mfHeight))

        RECORD_WINDOW.flushRecords()

        shellCmd = "minefield %d %d %d" % (mfWidth, mfHeight, nMines)
        LOG_WINDOW.push(shellCmd)
        SHELL.run(shellCmd)

        for o in SHELL.getOutput():
            LOG_WINDOW.push(o)

        TIMER.reset()

    @staticmethod
    def abortWithMessage(msg):

        curses.endwin()
        print(msg)
        sys.exit(1)

    @staticmethod
    def refreshDisplay():

        ROOT_SCREEN.noutrefresh()
        MINE_FIELD_WINDOW.updateAll()
        STATUS_WINDOW.updateAll()
        LOG_WINDOW.updateAll()
        RECORD_WINDOW.updateAll()
        curses.doupdate()

    @staticmethod
    def isRecordWindowActive():
        return RECORD_WINDOW.visible is True

    @staticmethod
    def isMineFieldResponsive():
        if TIMER.isRunning() is True:
            return True

        if TIMER.isReset() is True and GameControl.isRecordWindowActive() is False:
            return True

        return False

    @staticmethod
    def exit():
        if RECORD_WINDOW is not None:
            RECORD_WINDOW.flushRecords()
        sys.exit(0)

    @staticmethod
    def activateRecordWindow():
        RECORD_WINDOW.visible = True

        GameControl.pauseGame()

    @staticmethod
    def deactivateRecordWindow():
        RECORD_WINDOW.visible = False

    @staticmethod
    def toggleRecordWindow():
        if GameControl.isRecordWindowActive() is True:
            GameControl.deactivateRecordWindow()
        else:
            GameControl.activateRecordWindow()

    @staticmethod
    def resizeWindows():
        MINE_FIELD_WINDOW.resize()
        STATUS_WINDOW.resize()
        RECORD_WINDOW.resize()
        LOG_WINDOW.resize()

        if MINE_FIELD_WINDOW.isAbleToDrawMineField() is False:
            GameControl.pauseGame()

class EventLoop:

    def mineFieldOnMouseClick(self, mX, mY, btn):

        if TIMER.isPaused():
            return False

        coor = MINE_FIELD_WINDOW.retrieveMineFieldCoordinate(mX, mY)

        if coor is None:
            return False

        x, y = coor

        if btn == curses.BUTTON1_PRESSED:
            self.pokeCellOnMineField(x, y)

        elif btn == curses.BUTTON3_PRESSED:
            self.toggleCellOnMineField(x, y)

        else:
            pass

        return True

    def pokeCellOnMineField(self, x, y):

        if TIMER.isReset():
            TIMER.start()


        LOG_WINDOW.push("poke %d %d" % (x, y))
        SHELL.run("poke %d %d" % (x, y))
        for line in SHELL.getOutput():
            LOG_WINDOW.push(line)

        if MINE_FIELD_WINDOW.isBoomed() or MINE_FIELD_WINDOW.isFinished():
            TIMER.pause()

        if MINE_FIELD_WINDOW.isFinished():
            RECORD_WINDOW.updateRecord()
            self.bestRecordButtonOnMouseClick()

    def toggleCellOnMineField(self, x, y):

        LOG_WINDOW.push("toggle %d %d" % (x, y))
        SHELL.run("toggle %d %d" % (x, y))
        for line in SHELL.getOutput():
            LOG_WINDOW.push(line)


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

        GameControl.restartGame()

    def pauseGameButtonOnMouseClick(self):
        GameControl.togglePauseGame()

    def bestRecordButtonOnMouseClick(self):

        GameControl.toggleRecordWindow()

    def leaveButtonOnMouseClick(self):

        GameControl.exit()

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

                    GameControl.refreshDisplay()
                    continue

                if self.mineFieldOnMouseClick(mX, mY, btn) is True:

                    GameControl.refreshDisplay()
                    continue

            elif event == ord('q'):
                GameControl.exit()

            elif event == ord('n'):
                GameControl.deactivateRecordWindow()
                GameControl.restartGame()
                GameControl.refreshDisplay()

            elif event == ord('r'):
                GameControl.toggleRecordWindow()
                GameControl.refreshDisplay()

            elif event == ord('p'):
                GameControl.deactivateRecordWindow()
                GameControl.togglePauseGame()
                GameControl.refreshDisplay()

            elif event == ord(' '):
                if GameControl.isMineFieldResponsive() is True:
                    coor = MINE_FIELD_WINDOW.getCursor()
                    if coor is not None:
                        x, y = coor
                        self.pokeCellOnMineField(x, y)

                        GameControl.refreshDisplay()

            elif event == ord('f'):
                if GameControl.isMineFieldResponsive() is True:
                    coor = MINE_FIELD_WINDOW.getCursor()
                    if coor is not None:
                        x, y = coor
                        self.toggleCellOnMineField(x, y)

                        GameControl.refreshDisplay()

            elif event == ord('c'):
                if GameControl.isMineFieldResponsive() is True:
                    MINE_FIELD_WINDOW.toggleCursorVisible()

                    GameControl.refreshDisplay()

            elif event == curses.KEY_LEFT:
                if GameControl.isMineFieldResponsive() is True:
                    if MINE_FIELD_WINDOW.isCursorVisible() is True:
                        MINE_FIELD_WINDOW.translateCursor(-1, 0)

                        GameControl.refreshDisplay()

            elif event == curses.KEY_RIGHT:
                if GameControl.isMineFieldResponsive() is True:
                    if MINE_FIELD_WINDOW.isCursorVisible() is True:
                        MINE_FIELD_WINDOW.translateCursor(1, 0)

                        GameControl.refreshDisplay()

            elif event == curses.KEY_UP:
                if GameControl.isMineFieldResponsive() is True:
                    if MINE_FIELD_WINDOW.isCursorVisible() is True:
                        MINE_FIELD_WINDOW.translateCursor(0, -1)

                        GameControl.refreshDisplay()

            elif event == curses.KEY_DOWN:
                if GameControl.isMineFieldResponsive() is True:
                    if MINE_FIELD_WINDOW.isCursorVisible() is True:
                        MINE_FIELD_WINDOW.translateCursor(0, 1)

                        GameControl.refreshDisplay()

            elif event == curses.KEY_RESIZE:
                GameControl.resizeWindows()
                GameControl.refreshDisplay()

            else:
                pass

class ClockUpdater(threading.Thread):

    def run(self):
        while True:
            STATUS_WINDOW.updateClock()
            curses.doupdate()
            time.sleep(0.1)

def Main(screen):

    GameControl.initDisplay(screen)
    GameControl.initGame()

    GameControl.restartGame()

    clockUpdater = ClockUpdater()
    clockUpdater.daemon = True
    clockUpdater.start()

    GameControl.refreshDisplay()
    EventLoop().run()

if __name__ == '__main__':

    GameControl.initArguments()
    GameControl.initRC()

    if ARGUMENTS.needsListingRecord() is True:
        GameControl.dumpRecord()
        GameControl.exit()

    curses.wrapper(Main)
