import curses

LOG_WINDOW_WIDTH = 20

def cursesColor(colorStr):
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

class Style:

    def __init__(self, style=None, color=None):
        self._style = 0 if style is None else style
        self._color = color

    def attr(self):
        return self._style | cursesColor(self._color)

class StyledText:

    def __init__(self, text, style=None, color=None):
        self._text = text
        self._style = Style(style, color)

    def text(self):
        return self._text

    def attr(self):
        return self._style.attr()

CELL_DIGIT_NONE = StyledText('   ', 0)
CELL_DIGIT_1    = StyledText(' 1 ', curses.A_BOLD, 'blue')
CELL_DIGIT_2    = StyledText(' 2 ', 0, 'green')
CELL_DIGIT_3    = StyledText(' 3 ', curses.A_BOLD, 'red')
CELL_DIGIT_4    = StyledText(' 4 ', curses.A_BOLD, 'magenta')
CELL_DIGIT_5    = StyledText(' 5 ', 0, 'red')
CELL_DIGIT_6    = StyledText(' 6 ', 0, 'cyan')
CELL_DIGIT_7    = StyledText(' 7 ', 0, 'yellow')
CELL_DIGIT_8    = StyledText(' 8 ', curses.A_BOLD, 'white')

CELL_FLAGGED    = StyledText(' $ ', curses.A_REVERSE | curses.A_BOLD, 'white')
CELL_UNEXPLORED = StyledText('   ', curses.A_REVERSE | curses.A_DIM)

CELL_WRONG          = StyledText('!X!', curses.A_REVERSE | curses.A_BOLD, 'yellow')
CELL_UNFLAGGED_MINE = StyledText(' * ', curses.A_REVERSE)
CELL_BOOMED         = StyledText('BM!', curses.A_REVERSE | curses.A_BOLD, 'red')

MINE_FIELD_CELL_CHEIGHT = 1
MINE_FIELD_CELL_CWIDTH  = 3

MINE_FIELD_MARGIN_CHEIGHT = 2
MINE_FIELD_MARGIN_CWIDTH = 1

MINE_FIELD_BORDER_CHEIGHT = 1
MINE_FIELD_BORDER_CWIDTH = 1
MINE_FIELD_BORDER_DEFAULT_STYLE = Style()
MINE_FIELD_BORDER_BOOMED_STYLE = Style(curses.A_DIM, 'red')
MINE_FIELD_BORDER_FINISHED_STYLE = Style(curses.A_DIM, 'green')

MINE_FIELD_HEIGHT = 16
MINE_FIELD_WIDTH = 30
MINE_FIELD_MINES = 99
MINE_FIELD_DEFAULT_MINES_PERCENTAGE = 0.16

BUTTON_NEW_GAME = StyledText(' New Game ', curses.A_REVERSE, 'white')
BUTTON_PAUSE    = StyledText('  PAUSE  ', curses.A_REVERSE, 'white')
BUTTON_RECORDS  = StyledText(' RECORDS ', curses.A_REVERSE, 'white')

TIMER = StyledText(' %s ', curses.A_REVERSE, 'white')
MINES_REMAINING = StyledText(' %s ', curses.A_REVERSE, 'white')

SIDE_PANE_WIDTH = 32
SHELL_COMMAND_STYLE = 0
SHELL_OUTPUT_STYLE = 0
LOG_MESSAGE_STYLE = 0

LOG_BORDER_CHEIGHT = 1
LOG_BORDER_CWIDTH = 1

XAXIS_LABEL_STYLE = 0
YAXIS_LABEL_STYLE = 0

