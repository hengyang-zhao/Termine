import os
import curses

class Style:

    def __init__(self, style=None, color=None):
        self._style = 0 if style is None else style
        self._color = color

    def _cursesColor(self, colorStr):
        if colorStr is None:
            return 0

        colorStr = colorStr.lower()
        colorDict = {
                'red': 1,
                'green': 2,
                'yellow': 3,
                'blue': 4,
                'magenta': 5,
                'cyan': 6,
                'white': 7
        }
        return curses.color_pair(colorDict[colorStr])


    def attr(self):
        return self._style | self._cursesColor(self._color)

class StyledText:

    def __init__(self, text, style=None, color=None):
        self._text = text
        self._style = Style(style, color)

    def text(self):
        return self._text

    def attr(self):
        return self._style.attr()

class MineCellText(StyledText):

    def __init__(self, text, width, style=None, color=None):
        super().__init__(text, style, color)
        self._width = width

    def text(self):
        if len(self._text) < self._width:
            return self._text.center(self._width)

        else:

            cStart = (len(self._text) - self._width) // 2
            return self._text[cStart:cStart+self._width]

    def padding(self):
        return "".center(self._width)

class RCProvider:

    def __init__(self, **kwargs):

        self.MINE_FIELD_CELL_CWIDTH  = kwargs['mineFieldCellCWidth']
        self.MINE_FIELD_CELL_CHEIGHT = kwargs['mineFieldCellCHeight']

        self.MINE_FIELD_MARGIN_CHEIGHT = 1
        self.MINE_FIELD_MARGIN_CWIDTH = 1

        self.MINE_FIELD_BORDER_CHEIGHT = 1
        self.MINE_FIELD_BORDER_CWIDTH = 1
        self.MINE_FIELD_BORDER_DEFAULT_STYLE = Style()
        self.MINE_FIELD_BORDER_FOCUSED_STYLE = Style(curses.A_REVERSE, 'white')
        self.MINE_FIELD_BORDER_BOOMED_STYLE = Style(curses.A_DIM, 'red')
        self.MINE_FIELD_BORDER_FINISHED_STYLE = Style(curses.A_DIM, 'green')

        self.MINE_FIELD_TOO_SMALL_MESSAGE = StyledText(" VIEW PORT IS TOO SMALL ", curses.A_BOLD, 'white')

        self.MINE_FIELD_HEIGHT = 16
        self.MINE_FIELD_WIDTH = 30
        self.MINE_FIELD_MINES = 99
        self.MINE_FIELD_DEFAULT_MINES_PERCENTAGE = 0.16

        self.CELL_PAUSED     = MineCellText(' ~ ', self.MINE_FIELD_CELL_CWIDTH, curses.A_DIM | curses.A_REVERSE, 'white')

        self.CELL_DIGIT_NONE = MineCellText('   ', self.MINE_FIELD_CELL_CWIDTH, 0)
        self.CELL_DIGIT_1    = MineCellText(' 1 ', self.MINE_FIELD_CELL_CWIDTH, curses.A_BOLD, 'blue')
        self.CELL_DIGIT_2    = MineCellText(' 2 ', self.MINE_FIELD_CELL_CWIDTH, 0, 'green')
        self.CELL_DIGIT_3    = MineCellText(' 3 ', self.MINE_FIELD_CELL_CWIDTH, curses.A_BOLD, 'red')
        self.CELL_DIGIT_4    = MineCellText(' 4 ', self.MINE_FIELD_CELL_CWIDTH, curses.A_BOLD, 'magenta')
        self.CELL_DIGIT_5    = MineCellText(' 5 ', self.MINE_FIELD_CELL_CWIDTH, curses.A_DIM, 'red')
        self.CELL_DIGIT_6    = MineCellText(' 6 ', self.MINE_FIELD_CELL_CWIDTH, 0, 'cyan')
        self.CELL_DIGIT_7    = MineCellText(' 7 ', self.MINE_FIELD_CELL_CWIDTH, 0, 'yellow')
        self.CELL_DIGIT_8    = MineCellText(' 8 ', self.MINE_FIELD_CELL_CWIDTH, curses.A_BOLD, 'white')

        self.CELL_FLAGGED    = MineCellText(' $ ', self.MINE_FIELD_CELL_CWIDTH, curses.A_REVERSE | curses.A_BOLD, 'white')
        self.CELL_UNEXPLORED = MineCellText('   ', self.MINE_FIELD_CELL_CWIDTH, curses.A_REVERSE | curses.A_DIM)

        self.CELL_WRONG          = MineCellText('!X!', self.MINE_FIELD_CELL_CWIDTH, curses.A_REVERSE | curses.A_BOLD, 'red')
        self.CELL_UNFLAGGED_MINE = MineCellText(' * ', self.MINE_FIELD_CELL_CWIDTH, curses.A_REVERSE)
        self.CELL_BOOMED         = MineCellText('BM!', self.MINE_FIELD_CELL_CWIDTH, curses.A_REVERSE | curses.A_BOLD, 'yellow')

        # Status window properties

        self.BUTTON_NEW_GAME = StyledText(' New Game ', curses.A_REVERSE, 'white')
        self.BUTTON_PAUSE    = StyledText('  PAUSE  ', curses.A_REVERSE, 'white')
        self.BUTTON_RESUME   = StyledText(' UNPAUSE ', curses.A_REVERSE, 'white')
        self.BUTTON_RECORDS  = StyledText(' RECORDS ', curses.A_REVERSE, 'white')
        self.BUTTON_LEAVE    = StyledText('  LEAVE  ', curses.A_REVERSE, 'white')

        self.STATUS_TIMER = StyledText(' %s ', curses.A_REVERSE, 'white')
        self.STATUS_MINE_REMAINING = StyledText(' %s ', curses.A_REVERSE, 'white')

        # Side pane (log window) properties

        self.LOG_WINDOW_CWIDTH = 20
        self.LOG_BORDER_CHEIGHT = 1
        self.LOG_BORDER_CWIDTH = 1

        # Record window properties

        self.RECORD_WINDOW_CWIDTH = 60
        self.RECORD_WINDOW_CHEIGHT = 12
        self.RECORD_FILE_PATH = os.path.sep.join([os.environ['HOME'], '.termine_records'])
        self.RECORD_CURRENT_STYLE = Style(curses.A_BOLD, 'green')
        self.RECORD_DEFAULT_STYLE = Style(0, 'white')

        self.TERM_CWIDTH_LIMIT = 80
        self.TERM_CHEIGHT_LIMIT = 25

