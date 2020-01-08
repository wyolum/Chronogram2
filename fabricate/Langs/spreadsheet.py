import string
from numpy import *

class Spreadsheet:
    def __init__(self, lines):
        self.lines = lines

    def _getCell(self, row, col):
        out = None
        if row < len(self.lines):
            l = self.lines[row]
            if col < len(l):
                out = l[col]
        return out
    def getCell(self, cellstr):
        j, i = self.parsecell(cellstr)
        return self._getCell(j, i)
    def _getRegion(self, row, col, length, width):
        out = []
        i = row - 1
        while i < row + length:
            i += 1
            out.append([])
            j = col - 1
            while j < col + width:
                j += 1
                next = self._getCell(i, j)
                if next is not None:
                    out[-1].append(next)
                else:
                    break
            if length == inf and len(out[-1]) == 0:
                break
        return out
    @staticmethod
    def parsecell(cell_str):
        cell_str = cell_str.upper()
        i = 0
        if cell_str[0] == '*':
            col = inf
        else:
            col = ord(cell_str[0]) - ord('A') + 1
            for i, l in enumerate(cell_str[1:]):
                if l in string.ascii_uppercase:
                    col = col * 26  + ord(l) - ord('A') + 1
                else:
                    break
        if cell_str[i + 1:] == '*':
            row = inf
        else:
            row = int(cell_str[i + 1:])
        return row - 1, col - 1
        
    def getRegion(self, reg_str):
        'examples  r11, R11:Q23 R11:R23 R11:R*  R11:*11 R11:**'
        reg_str = reg_str.upper()
        if ':' in reg_str:
            start, stop = [self.parsecell(x) for x in reg_str.split(':')]
            out = self._getRegion(start[0], start[1], 
                                  stop[0] - start[0], stop[1] - start[1])
        else:
            out = [[self._getCell(*self.parsecell(reg_str))]]
        return out
    def __getitem__(self, cell_str):
        return self.getCell(cell_str)
    
