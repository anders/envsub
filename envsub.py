#!/usr/bin/env python2.7
# encoding: utf-8
#
# envsub -- simple templating for configuration files based on ENV
# Copyright (C) 2015 Anders Bergh <anders1@gmail.com>
# Idea based on https://github.com/kreuzwerker/envplate.

import argparse
import glob
import os
import re
import shutil


PATTERN = re.compile(r'\$\{(.+?)(?:\:\-(.+?))?\}')


def main():
    parser = argparse.ArgumentParser(description='replace env keys in files')
    parser.add_argument('files', metavar='FILE', type=str, nargs='+',
                        help='configuration files to process')
    parser.add_argument('-g', '--glob', action='store_true',
                        help='glob passed filenames')
    parser.add_argument('-b', '--backup', action='store_true',
                        help='save original files with .bak suffix')
    parser.add_argument('-v', '--verbose', action='store_true',
                        help='enable verbose output')
    parser.add_argument('-e', '--execute', nargs=argparse.REMAINDER,
                        help='run external command')
    parser.add_argument('-s', '--strict', action='store_true',
                        help='error on missing environment variables')

    args = parser.parse_args()

    if args.glob:
        files = []
        for path in args.files:
            globbed = glob.glob(path)
            if not globbed:
                parser.error('could not glob {}'.format(path))
            files += globbed
        args.files = files
    else:
        for path in args.files:
            if not os.path.exists(path):
                parser.error('{}: no such file'.format(path))

    for path in args.files:
        if args.backup:
            backup_path = path + '.bak'
            # should it check if it would overwrite a file?
            shutil.copyfile(path, backup_path)

        with open(path, 'r+b') as f:
            data = f.read()

            def sub_cb(match):
                key, default = match.group(1, 2)
                value = default
                if key in os.environ:
                    value = os.environ[key]

                if not value and args.strict:
                    parser.error('env \'{}\' is not set'.format(key))

                return value

            output, substitutions = PATTERN.subn(sub_cb, data)
            f.seek(0)
            f.write(output)
            f.truncate()

            if args.verbose:
                print('{}: {} substitutions'.format(path, substitutions))

    if args.execute:
        os.execvp(args.execute[0], args.execute)

if __name__ == '__main__':
    main()
