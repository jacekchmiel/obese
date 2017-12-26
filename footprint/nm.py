import re
from enum import Enum

_line_pattern = re.compile(r'(?:([0-9a-f]+) )?(?:([0-9a-f]+) )?([\w]) (.*)')


class SymbolType(Enum):
    Text = ord('t')
    Weak = ord('w')
    UninitializedData = ord('b')
    ReadOnlyData = ord('r')
    Data = ord('d')
    Undefined = ord('u')
    Debug = ord('n')
    Absolute = ord('a')

    @staticmethod
    def from_chr(char):
        c = char.lower()
        if c == 'v':
            c = 'w'

        return SymbolType(ord(c))


class Symbol:
    def __init__(self, addr, size, type, name):
        self.name = name
        self.type = type
        self.size = size
        self.addr = addr

    def __str__(self):
        if self.size is not None:
            return '{} - {}B'.format(self.name, self.size)
        else:
            return self.name


def parse_line(line):
    if type(line) is bytes:
        line = line.decode('utf8').strip()
    m = _line_pattern.match(line)
    address = int(m.group(1), 16) if m.group(1) else None
    size = int(m.group(2), 16) if m.group(2) else None

    name = m.group(4)
    return Symbol(address, size, SymbolType.from_chr(m.group(3)), name)

    # name = tokens[-1].decode('utf8')
    # type = tokens[-2].decode('utf8')
    #
    # if len(tokens) > 4:
    #     raise ValueError("Too many tokens")
    #
    # if len(tokens) >= 3:
    #     addr = int(tokens[0], 16)
    # else:
    #     addr = None
    #
    # if len(tokens) == 4:
    #     size = int(tokens[1], 16)
    # else:
    #     size = 0
    # return NmEntry(addr=addr, size=size, type=type, name=name)
