import unittest
from . import nm
from nose.tools import *


class LineParsingTest(unittest.TestCase):
    def test_extracts_address(self):
        symbol = nm.parse_line(b'00031456 00000010 t ._433')
        assert_equal(symbol.addr, int(b'00031456', 16))

    def test_extracts_size(self):
        symbol = nm.parse_line(b'00031456 00000010 t ._433')
        assert_equal(symbol.size, 16)

    def test_extracts_name(self):
        symbol = nm.parse_line(b'00031456 00000010 t ._433')
        assert_equal(symbol.name, '._433')

    def test_extracts_type(self):
        symbol = nm.parse_line(b'00031456 00000010 t ._433')
        assert_equal(symbol.type, nm.SymbolType.Text)

    def test_parses_symbol_without_size(self):
        symbol = nm.parse_line(b'0002fbe1 T __aeabi_drsub')
        assert_equal(symbol.addr, int(b'0002fbe1', 16))
        assert_is_none(symbol.size)
        assert_equal(symbol.name, '__aeabi_drsub')
        assert_equal(symbol.type, nm.SymbolType.Text)

    def test_parses_symbol_without_size_and_address(self):
        symbol = nm.parse_line(b'w atexit')
        assert_is_none(symbol.addr)
        assert_is_none(symbol.size)
        assert_equal(symbol.name, 'atexit')
        assert_equal(symbol.type, nm.SymbolType.Weak)

    def test_data_symbol_is_parsed(self):
        symbol = nm.parse_line('20004000 d $d')
        assert_equal(symbol.type, nm.SymbolType.Data)

    def test_readonly_data_symbol_is_parsed(self):
        symbol = nm.parse_line('00002000 r Heap_Size')
        assert_equal(symbol.type, nm.SymbolType.ReadOnlyData)

    def test_uninitialized_data_symbol_is_parsed(self):
        symbol = nm.parse_line('200091a0 B __bss_end__')
        assert_equal(symbol.type, nm.SymbolType.UninitializedData)

    def test_undefined_symbol_is_parsed(self):
        symbol = nm.parse_line('U __cxa_begin_cleanup')
        assert_equal(symbol.type, nm.SymbolType.Undefined)

    def test_debug_symbol_is_parsed(self):
        symbol = nm.parse_line('200091a0 n $d')
        assert_equal(symbol.type, nm.SymbolType.Debug)
