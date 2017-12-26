#!/usr/bin/env python3
import argparse

import subprocess
from operator import itemgetter, attrgetter

from . import nm


def by_file(symbols):
    tree = {}
    for s in symbols:
        f = s.source.file if s.has_source() else None
        try:
            tree[f]['symbols'].append(s)
            tree[f]['total_size'] += s.size
        except KeyError:
            tree[f] = {'symbols': [s], 'total_size': s.size}
    return tree


def print_by_file(header, symbols):
    print(header)
    print('=' * len(header))
    tree = by_file(symbols)
    sorted_by_size = sorted(tree.items(), key=lambda v: v[1]['total_size'], reverse=True)
    for path, data in sorted_by_size:
        print(data['total_size'], path)
        for s in sorted(data['symbols'], key=attrgetter('size'), reverse=True):
            print('\t', s.size, s.name)
            print('\t\t', s.original)

    print()


def main():
    p = argparse.ArgumentParser()
    p.add_argument('executable', type=str)
    args = p.parse_args()

    nm_out = subprocess.check_output(['nm', '--demangle', '--print-size', '--line-numbers', args.executable])
    symbols = []
    for line in nm_out.splitlines():
        try:
            sym = nm.parse_line(line)
            if sym.has_size():
                symbols.append(sym)
                # print(sym)
        except BaseException:
            print('Exception raised during paring nm line:')
            print(str(line.strip()))
            raise

    print()
    print('Parsed {} lines'.format(len(nm_out.splitlines())))
    print('{} symbols have size'.format(len(symbols)))
    print()

    data_symbols = [s for s in symbols if
                    s.type in (nm.SymbolType.Data, nm.SymbolType.ReadOnlyData, nm.SymbolType.UninitializedData)]
    code_symbols = [s for s in symbols if s.type is nm.SymbolType.Text]
    other_symbols = [s for s in symbols if s.type not in
                     (nm.SymbolType.Data, nm.SymbolType.ReadOnlyData,
                      nm.SymbolType.UninitializedData, nm.SymbolType.Text)]

    print_by_file('Data Symbols', data_symbols)
    print_by_file('Code Symbols', code_symbols)
    print_by_file('Other Symbols', other_symbols)


if __name__ == '__main__':
    main()
