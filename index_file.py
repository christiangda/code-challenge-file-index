#!/usr/bin/env python3
import argparse
from datetime import datetime
import re

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

Regex groups:
# \" together
([^\"](?<=\\)\") --> https://regex101.com/r/eYZzNh/11

#Everuthings inside " "
([^\"](?<=\\)\")(.+)(\1)     --> https://regex101.com/r/eYZzNh/12

#Everuthings inside " " except (\"\r\n\t\f\v)
^(\")([^\"\r\n\t\f\v]+)(\1)$ --> https://regex101.com/r/eYZzNh/13

# Content inside quotes except "
^(?P<quoted>\")([^\"\r\n\t\f\v]+)(?P=quoted)$ --> https://regex101.com/r/eYZzNh/14

([^\"](?<=\\)\")(.+)(\1)

# only numbers > 0
([1-9][0-9]*) --> https://regex101.com/r/eYZzNh/4

# white spaces and at least 1
( +)          --> https://regex101.com/r/eYZzNh/5

# only characters 0..9 and - and : and at least 1
([0-9\-\:]+)  --> https://regex101.com/r/eYZzNh/6

# words without white character + white space
^([^\\\"\r\n\t\f\v]+)$  --> https://regex101.com/r/eYZzNh/7

# Any non (white space and "), bassically words
([^\" ]+)                          --> https://regex101.com/r/eYZzNh/3

# Any work inside "", including those (using lookahead and lookbehind)
^(?=\")([^\s].*)(?<=\")$           --> https://regex101.com/r/eYZzNh/1

# the previous two together ((only words without ")|(quoted words))
(([^\" ]+)|(?=\")([^\s].*)(?<=\")) --> https://regex101.com/r/eYZzNh/2

# Repetition of (( +)((only words without ")|(quoted words))){3}
(( +)(([^\" ]+)|(?=\")([^\s].*)(?<=\"))){3} -->

# The pattern solution
^([1-9][0-9]*)( +)([0-9\-\:]+)(( +)(([^\" ]+)|(?P<q>(?<![\\])[\"])((?:.(?!(?<![\\])(?P=q)))*.?)(?P=q))){3}$


# Get groups with words
^([1-9][0-9]*)( +)([0-9\-\:]+)( +)([^\"\s]+)( +)([^\"\s]+)( +)([^\"\s]+)$

# Get groups with quotes ans spaces
^([1-9][0-9]*)( +)([0-9\-\:]+)( +)((?P<q1>\")([^\"\r\n\t\f\v]+)(?P=q1))( +)((?P<q2>\")([^\"\r\n\t\f\v]+)(?P=q2))( +)((?P<q3>\")([^\"\r\n\t\f\v]+)(?P=q3))$

(?P<q1>\")([^\"\r\n\t\f\v]+)(?P=q1)


# Best solution until now
https://regex101.com/r/eYZzNh/16
^([1-9][0-9]*)( +)([0-9\-\:]+)( +)((?P<q1>\")([^\"\r\n\t\f\v]+)(?P=q1)|([^\\\"\s]+))( +)((?P<q2>\")([^\"\r\n\t\f\v]+)(?P=q2)|([^\\\"\s]+))( +)((?P<q3>\")([^\"\r\n\t\f\v]+)(?P=q3)|([^\\\"\s]+))$
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
                if fields[1] in database:
                    database[fields[1]].append(fields[10])
                else:
                    database[fields[1]] = list()
                    database[fields[1]].append(fields[10])
            else:
                errors += 1
    return errors


def validate(line):
    fields = split_line(line)
    # print(fields)
    valid_key = True
    valid_datetime = True
    valid_size = False

    if len(fields) > 1:
        valid_size = True
        try:
            if int(fields[1]) < 1:
                raise ValueError('key is negative value')
        except ValueError:
            valid_key = False

        try:
            datetime.strptime(fields[3], "%Y-%m-%d-%H:%M:%S")
        except ValueError:
            valid_datetime = False

    #print('{},{},{},{}'.format(valid_key, valid_datetime, valid_size, fields))
    return (valid_key and valid_datetime and valid_size), fields


def split_line(line):
    pattern = r"""^([1-9][0-9]*)( +)([0-9\-\:]+)( +)((?P<q1>\")([^\"\r\n\t\f\v]+)(?P=q1)|([^\\\"\s]+))( +)((?P<q2>\")([^\"\r\n\t\f\v]+)(?P=q2)|([^\\\"\s]+))( +)((?P<q3>\")([^\"\r\n\t\f\v]+)(?P=q3)|([^\\\"\s]+))$"""

    pattern_string = r"""
        ^                                       #--> start
        ([1-9][0-9]*)                           #--> only positive numbers
        ( +)                                    #--> one o more white spaces
        ([0-9\-\:]+)
        ( +)                                    #--> one o more white spaces
        (                                       #--> start group of single word or quoted word
            (?P<q1>\")([^\"\r\n\t\f\v]+)(?P=q1) #--> quoted word
            |                                   #--> or condition
            ([^\\\"\s]+)                        #--> single word
        )                                       #--> start group of single word or quoted word
        ( +)                                    #--> one o more white spaces
        (
            (?P<q2>\")([^\"\r\n\t\f\v]+)(?P=q2) #--> quoted word
            |                                   #--> or condition
            ([^\\\"\s]+)                        #--> single word
        )                                       #--> start group of single word or quoted word
        ( +)                                    #--> one o more white spaces
        (
            (?P<q3>\")([^\"\r\n\t\f\v]+)(?P=q3) #--> quoted word
            |                                   #--> or condition
            ([^\\\"\s]+))                       #--> single word
        $                                       #--> end
    """

    field_list = re.split(pattern, line)
    #print('sieze: {},  data: {}'.format(len(field_list), field_list))
    return field_list


if __name__ == "__main__":
    """
    my memory structure is a dict where key is a int and value is a list:
    { ID :[String1, String2, String2]}
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

    index_text = input("Enter a list of indexes separate by commas (,)?")
    index_list = index_text.split(',')
    for index in index_list:
        if index in mem_structure:
            for value in mem_structure[index]:
                print('{} {}'.format(index, value))
        else:
            print('{} --> key does not exit'.format(index))
