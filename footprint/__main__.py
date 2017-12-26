#!/usr/bin/env python3
import argparse

import subprocess
from . import nm


def main():
    p = argparse.ArgumentParser()
    p.add_argument('executable', type=str)
    args = p.parse_args()

    nm_out = subprocess.check_output(['nm', '-CS', args.executable])
    for line in nm_out.splitlines():
        try:
            print(nm.parse_line(line))
        except BaseException:
            print('Exception raised during paring nm line:')
            print(str(line.strip()))
            raise

    print()
    print('Parsed {} lines'.format(len(nm_out.splitlines())))


if __name__ == '__main__':
    main()
