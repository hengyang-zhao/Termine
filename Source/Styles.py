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

