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
            tree['symbols'].append(s)
            tree[f]['total_size'] += s.size
        except KeyError:
            tree[f] = {'symbols': [s], 'total_size': s.size}
    return tree


def insert_symbol_rec(tree, namespaces, symbol):
    tree['total_size'] += symbol.size

    try:
        top_namespace = namespaces[0]
    except IndexError:
        return  # no more children

    subnamespaces = namespaces[1:]

    try:
        child = tree['children'][top_namespace]
    except KeyError:
        child = {'total_size': 0, 'children': {}, 'name': top_namespace}
        tree['children'][top_namespace] = child

    insert_symbol_rec(child, subnamespaces, symbol)


def _split_namespaces(name):
    tokens = name.split('::')
    out = []
    braces = []
    for t in tokens:
        if braces:
            out[-1] += '::' + t
        else:
            out.append(t)

        if '<' in t:
            braces.append('<')

        if '(' in t:
            braces.append('(')

        if '>' in t:
            braces.pop()

        if ')' in t:
            braces.pop()
    return out


def by_namespace(symbols):
    tree = {'total_size': 0, 'children': {}, 'name': ''}
    for s in symbols:
        names = _split_namespaces(s.name)
        insert_symbol_rec(tree, names, s)
    return tree


def print_tree(tree, *, max_depth=0, depth=0, prefix=''):
    if max_depth <= 0 or depth <= max_depth:
        print('{}{} {}{}'.format('  ' * depth, tree['total_size'], prefix, tree['name']))

        for c in sorted(tree['children'].values(), key=itemgetter('total_size'), reverse=True):
            child_prefix = prefix + tree['name'] + '::' if prefix + tree['name'] else tree['name']
            print_tree(c, max_depth=max_depth, depth=depth + 1, prefix=child_prefix)


def print_by_file(header, symbols):
    tree = by_file(symbols)

    print(header)
    print('=' * len(header))
    print('Total size: {}'.format(sum(s['total_size'] for s in tree.values())))
    print()

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
    p.add_argument('symbols', type=str, choices=('code', 'data', 'other'))
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

    code_by_namespace = by_namespace(code_symbols)
    data_by_namespace = by_namespace(data_symbols)
    other_by_namespace = by_namespace(other_symbols)

    if symbols == 'code':
        print_tree(code_by_namespace)
    elif symbols == 'data':
        print_tree(data_by_namespace)
    else:
        print_tree(other_by_namespace)

    # print_by_file('Data Symbols', data_symbols)
    # print_by_file('Code Symbols', code_symbols)
    # print_by_file('Other Symbols', other_symbols)


if __name__ == '__main__':
    main()
