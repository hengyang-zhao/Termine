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

class Cell:

    def __init__(self, text, style=None, color=None):
        self._text = text
        self._style = 0 if style is None else style
        self._color = color

    def text(self):
        return self._text

    def attr(self):
        return self._style | cursesColor(self._color)

CELL_DIGIT_NONE = Cell('   ', 0)
CELL_DIGIT_1    = Cell(' 1 ', curses.A_BOLD, 'blue')
CELL_DIGIT_2    = Cell(' 2 ', 0, 'green')
CELL_DIGIT_3    = Cell(' 3 ', curses.A_BOLD, 'red')
CELL_DIGIT_4    = Cell(' 4 ', curses.A_BOLD, 'magenta')
CELL_DIGIT_5    = Cell(' 5 ', 0, 'red')
CELL_DIGIT_6    = Cell(' 6 ', 0, 'cyan')
CELL_DIGIT_7    = Cell(' 7 ', 0, 'yellow')
CELL_DIGIT_8    = Cell(' 8 ', curses.A_BOLD, 'white')

CELL_FLAGGED    = Cell(' $ ', curses.A_REVERSE | curses.A_BOLD, 'white')
CELL_UNEXPLORED = Cell('   ', curses.A_REVERSE | curses.A_DIM)

CELL_WRONG          = Cell('!X!', curses.A_REVERSE | curses.A_BOLD, 'yellow')
CELL_UNFLAGGED_MINE = Cell(' * ', curses.A_REVERSE)
CELL_BOOMED         = Cell('BM!', curses.A_REVERSE | curses.A_BOLD, 'red')

MINE_FIELD_CELL_CHEIGHT = 1
MINE_FIELD_CELL_CWIDTH  = 3

MINE_FIELD_MARGIN_CHEIGHT = 2
MINE_FIELD_MARGIN_CWIDTH = 1

MINE_FIELD_BORDER_CHEIGHT = 1
MINE_FIELD_BORDER_CWIDTH = 1

MINE_FIELD_HEIGHT = 16
MINE_FIELD_WIDTH = 30
MINE_FIELD_MINES = 99
MINE_FIELD_DEFAULT_MINES_PERCENTAGE = 0.16

SIDE_PANE_WIDTH = 32
SHELL_COMMAND_STYLE = 0
SHELL_OUTPUT_STYLE = 0
LOG_MESSAGE_STYLE = 0

LOG_BORDER_CHEIGHT = 1
LOG_BORDER_CWIDTH = 1

XAXIS_LABEL_STYLE = 0
YAXIS_LABEL_STYLE = 0

