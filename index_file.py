#!/usr/bin/env python3
import argparse
from datetime import datetime

"""
7 2016-06-10-17:53:22 "A quoted string we don't care about" "The string we do
care about." "Another string we don't care about with escaped\" \" quotes. "
8 2016-06-10-17:53:22 Str1 Value Str3
8 2016-06-10-17:53:22 Str1 Value Str3
8 2016-06-10-17:53:22 Str1 Value2 Str3
9 2016-06-10-17:53:22 Str1 Value2 Str3
-1 2016-06-10-17:53:22 "This line is invalid" Str2 Str3
10 2016-06-10 17:53:22 "Also invalid" Str2 Str3
10 2016-06-10-17:53:22 "Also invalid" Str2

Regex groups
([ ]+)                    --> white spaces 1 or +
(?P<index>[1-9]+)         --> only numbers > 0
(?P<datetime>[0-9\-\:])   -->
(?P<quote>(?<![\\])[\"])  --> match " , not match \"
([^\"]\S+)                --> Any non white space character except "

((?<![\\])['"])((?:.(?!(?<![\\])\1))*.?)\1 --> "sfasfadsa dsfasdf asf\" a"

(?P<quote>(?<![\\])["])((?:.(?!(?<![\\])(?P=quote)))*.?)(?P=quote)

((?P<quote>(?<![\\])["])((?:.(?!(?<![\\])(?P=quote)))*.?)(?P=quote)|([^\"]\S+)) --> "sdfdsfsdf" | sfasasdasd

# string
^([1-9]+)( +)([0-9\-\:]+)(( +)((?P<q>(?<![\\])[\"])((?:.(?!(?<![\\])(?P=q)))*.?)(?P=q)|([^\"]\S+))){3}$
"""


def main():
    parser = argparse.ArgumentParser(description='Process some file')
    parser.add_argument(
        '--input_file', '-f',
        type=argparse.FileType('r', encoding='UTF-8'),
        required=True,
        help='Input File'
    )

    args = parser.parse_args()
    return args.input_file


def index(file, database):
    errors = 0
    with file as f:
        for line in f.readlines():
            is_valid, fields = validate(line)
            if is_valid:
                if fields[0] in database:
                    database[fields[0]].append(fields[3])
                else:
                    database[fields[0]] = list()
                    database[fields[0]].append(fields[3])
            else:
                errors += 1
    return errors


def validate(line):
    fields = line.split()
    print(fields)
    valid_key = True
    valid_datetime = True

    try:
        if int(fields[0]) < 1:
            raise ValueError('key is negative value')
    except ValueError:
        valid_key = False

    try:
        datetime.strptime(fields[1], "%Y-%m-%d-%H:%M:%S")
    except ValueError:
        valid_datetime = False

    # print('{},{},{}'.format(valid_key, valid_datetime, fields[2]))

    return (valid_key and valid_datetime), fields


if __name__ == "__main__":
    """
    mem structure is a dict where key is a int and value is a list:
    { key :[String1, String2, String2]}
    {
       1: ['String1', 'String2', 'String2'],
      14: ['String1', 'String2', 'String3']
    }
    """
    mem_structure = dict()
    in_file = main()
    errors = index(in_file, mem_structure)
    in_file.close()
    print('================')
    print('Invalid lines: {}'.format(errors))
    print(mem_structure)

    index_text = input("Enter a list of indexes separate by commas (,)?")
    index_list = index_text.split(',')
    for index in index_list:
        if index in mem_structure:
            for value in mem_structure[index]:
                print('{} {}'.format(index, value))
        else:
            print('{} --> does not exit'.format(index))
