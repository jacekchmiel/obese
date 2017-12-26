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


class Source:
    def __init__(self, filename, line_number):
        self.file = filename
        self.line = line_number


class Symbol:
    def __init__(self, *, address: int, size: int, symbol_type: SymbolType, name: str, source: Source, original: str):
        self.name = name
        self.type = symbol_type
        self.size = size
        self.address = address
        self.source = source
        self.original = original

    def __str__(self):
        size_suffix = ' {}B'.format(self.size) if self.size is not None else ''
        source_suffix = ' from {}'.format(self.source) if self.source else ''
        return '<{}>{}{}'.format(self.name, size_suffix, source_suffix)

    def has_size(self):
        return self.size is not None

    def has_source(self):
        return self.source is not None


def parse_line(line):
    if type(line) is bytes:
        line = line.decode('utf8').strip()
    m = _line_pattern.match(line)
    address = int(m.group(1), 16) if m.group(1) else None
    size = int(m.group(2), 16) if m.group(2) else None
    symbol_type = SymbolType.from_chr(m.group(3))

    name, _, source_info = m.group(4).partition('\t')
    if source_info != '':
        filename, _, line_number = source_info.partition(':')
        source = Source(filename, line_number)
    else:
        source = None

    return Symbol(address=address, size=size, symbol_type=symbol_type, name=name, source=source, original=line.strip())
