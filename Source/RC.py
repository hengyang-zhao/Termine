import os
import curses

from Styles import *

# Mine field window properties

MINE_FIELD_CELL_CHEIGHT = 3
MINE_FIELD_CELL_CWIDTH  = 5

MINE_FIELD_MARGIN_CHEIGHT = 1
MINE_FIELD_MARGIN_CWIDTH = 1

MINE_FIELD_BORDER_CHEIGHT = 1
MINE_FIELD_BORDER_CWIDTH = 1
MINE_FIELD_BORDER_DEFAULT_STYLE = Style()
MINE_FIELD_BORDER_BOOMED_STYLE = Style(curses.A_DIM, 'red')
MINE_FIELD_BORDER_FINISHED_STYLE = Style(curses.A_DIM, 'green')

MINE_FIELD_TOO_SMALL_MESSAGE = StyledText(" VIEW PORT IS TOO SMALL ", curses.A_BOLD, 'white')

MINE_FIELD_HEIGHT = 16
MINE_FIELD_WIDTH = 30
MINE_FIELD_MINES = 99
MINE_FIELD_DEFAULT_MINES_PERCENTAGE = 0.16

CELL_PAUSED     = MineCellText(' ~ ', curses.A_DIM | curses.A_REVERSE, 'white')

CELL_DIGIT_NONE = MineCellText('   ', MINE_FIELD_CELL_CWIDTH, 0)
CELL_DIGIT_1    = MineCellText(' 1 ', MINE_FIELD_CELL_CWIDTH, curses.A_BOLD, 'blue')
CELL_DIGIT_2    = MineCellText(' 2 ', MINE_FIELD_CELL_CWIDTH, 0, 'green')
CELL_DIGIT_3    = MineCellText(' 3 ', MINE_FIELD_CELL_CWIDTH, curses.A_BOLD, 'red')
CELL_DIGIT_4    = MineCellText(' 4 ', MINE_FIELD_CELL_CWIDTH, curses.A_BOLD, 'magenta')
CELL_DIGIT_5    = MineCellText(' 5 ', MINE_FIELD_CELL_CWIDTH, curses.A_DIM, 'red')
CELL_DIGIT_6    = MineCellText(' 6 ', MINE_FIELD_CELL_CWIDTH, 0, 'cyan')
CELL_DIGIT_7    = MineCellText(' 7 ', MINE_FIELD_CELL_CWIDTH, 0, 'yellow')
CELL_DIGIT_8    = MineCellText(' 8 ', MINE_FIELD_CELL_CWIDTH, curses.A_BOLD, 'white')

CELL_FLAGGED    = MineCellText(' $ ', MINE_FIELD_CELL_CWIDTH, curses.A_REVERSE | curses.A_BOLD, 'white')
CELL_UNEXPLORED = MineCellText('   ', MINE_FIELD_CELL_CWIDTH, curses.A_REVERSE | curses.A_DIM)

CELL_WRONG          = MineCellText('!X!', MINE_FIELD_CELL_CWIDTH, curses.A_REVERSE | curses.A_BOLD, 'red')
CELL_UNFLAGGED_MINE = MineCellText(' * ', MINE_FIELD_CELL_CWIDTH, curses.A_REVERSE)
CELL_BOOMED         = MineCellText('BM!', MINE_FIELD_CELL_CWIDTH, curses.A_REVERSE | curses.A_BOLD, 'yellow')

# Status window properties

BUTTON_NEW_GAME = StyledText(' New Game ', curses.A_REVERSE, 'white')
BUTTON_PAUSE    = StyledText('  PAUSE  ', curses.A_REVERSE, 'white')
BUTTON_RESUME   = StyledText(' UNPAUSE ', curses.A_REVERSE, 'white')
BUTTON_RECORDS  = StyledText(' RECORDS ', curses.A_REVERSE, 'white')
BUTTON_LEAVE    = StyledText('  LEAVE  ', curses.A_REVERSE, 'white')

STATUS_TIMER = StyledText(' %s ', curses.A_REVERSE, 'white')
STATUS_MINE_REMAINING = StyledText(' %s ', curses.A_REVERSE, 'white')

# Side pane (log window) properties

LOG_WINDOW_CWIDTH = 20
LOG_BORDER_CHEIGHT = 1
LOG_BORDER_CWIDTH = 1

# Record window properties

RECORD_WINDOW_CWIDTH = 60
RECORD_WINDOW_CHEIGHT = 12
RECORD_FILE_PATH = os.path.sep.join([os.environ['HOME'], '.termine_records'])
RECORD_CURRENT_STYLE = Style(curses.A_BOLD, 'green')
RECORD_DEFAULT_STYLE = Style(0, 'white')

TERM_CWIDTH_LIMIT = 80
TERM_CHEIGHT_LIMIT = 25

