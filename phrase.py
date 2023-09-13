#!/usr/bin/env python
# -*- coding:utf-8 -*-

import csv
import json
import os
import random
import re
import sys
import time
import traceback

from datetime import datetime
from tts import LocalTts as Tts
from utils import remove, reprDict, runCommand, getch, getchar, getPathnames, getProperty, prGreen, prRed, prYellow, prLightPurple, prPurple, prCyan, prLightGray, prBlack, stdinReadline


class Phrase:

    NOUN_REGEX = r'[ \t]([nm][,\.]*)[^a-zA-Z]+'
    VERB_REGEX = r'[ \t]([vuw][,\.]*)[^a-zA-Z]+'
    VI_REGEX = r'[ \t]([vuw]i[,\.]*)[^a-zA-Z]+'
    VT_REGEX = r'[ \t]([vuw]t[,\.]*)[^a-zA-Z]+'
    ADJ_REGEX = r'[ \t](ad[ij:;][,\.]*)[^a-zA-Z]+'
    ADV_REGEX = r'[ \t](ad[vyu][,\.]*)[^a-zA-Z]+'
    PREP_REGEX = r'[ \t](prep[,\.]*)[^a-zA-Z]+'

    PHRASE_DICT = {
        'noun': {
            'regex': NOUN_REGEX,
            'exp': 'n.'
        },
        'verb': {
            'regex': VERB_REGEX,
            'exp': 'v.'
        },
        'vi': {
            'regex': VI_REGEX,
            'exp': 'vi.'
        },
        'vt': {
            'regex': VT_REGEX,
            'exp': 'vt.'
        },
        'adjective': {
            'regex': ADJ_REGEX,
            'exp': 'adj.'
        },
        'adv': {
            'regex': ADV_REGEX,
            'exp': 'adv.'
        },
        'prep': {
            'regex': PREP_REGEX,
            'exp': 'prep.'
        }
    }

    # Return a list of positions
    @staticmethod
    def find(string, phrase):

        positions = []

        regex = phrase['regex']

        matches = re.finditer(regex, string, re.MULTILINE)

        for matchNum, match in enumerate(matches, start=1):

            for groupNum in range(0, len(match.groups())):
                groupNum = groupNum + 1
                position = (match.start(groupNum), match.end(groupNum))
                positions.append(position)

        if len(positions) == 0:
            return None

        return positions

    @staticmethod
    def findall(string):
        # Add a blank in front of the line
        string = ' ' + string

        positions = []

        for key in Phrase.PHRASE_DICT.keys():
            phrase = Phrase.PHRASE_DICT[key]

            phrasePositions = Phrase.find(string, phrase)
            if not phrasePositions:
                continue

            for start, end in phrasePositions:
                positions.append((start - 1, end - 1))

        if len(positions) == 0:
            return None

        return sorted(positions)

    @staticmethod
    def replaceall(string):
        # Add a blank in front of the line
        string = ' ' + string

        for key in Phrase.PHRASE_DICT.keys():
            phrase = Phrase.PHRASE_DICT[key]

            positions = Phrase.find(string, phrase)
            if not positions:
                continue

            lastEnd = 0
            temp = ''

            for start, end in positions:
                temp += string[lastEnd:start] + phrase['exp']
                lastEnd = end
            else:
                temp += string[lastEnd:]

            string = temp

        return string[1:]  # remove the blank


class Explanation:

    REGEX = r"([^a-zA-Z0-9$ %'])"

    # Find the first one
    @staticmethod
    def find(string):

        matches = re.finditer(Explanation.REGEX, string, re.MULTILINE)

        for matchNum, match in enumerate(matches, start=1):

            for groupNum in range(0, len(match.groups())):
                groupNum = groupNum + 1
                return match.start(groupNum)

        return -1


class Sentence:

    # Find the first one
    @staticmethod
    def refine(string):

        string = Phrase.replaceall(string)
        positions = Phrase.findall(string)

        if positions is not None:
            start, end = positions[0]
            return string[:start], string[start:]

        position = Explanation.find(string)
        if position > 0:
            return string[:position], string[position:]

        return string, None


def run(name, configFile):

    try:
        prGreen('Now: {}'.format(datetime.now().strftime('%Y-%m-%d %H:%M:%S')))

        filename = 'english/synonym/9988/unit-b6-1.txt'
        with open(filename) as fp:
            lines = fp.read().splitlines()

            for line in lines:
                print(Sentence.refine(line))

    except KeyboardInterrupt:
        pass
    except Exception as e:
        prRed('Error occurs at {}'.format(
            datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
        traceback.print_exc(file=sys.stdout)
    finally:
        pass


def main(argv):

    if len(argv) < 2:
        print('Usage:\n\t', argv[0], '[config-file]\n')

    os.environ['TZ'] = 'Asia/Shanghai'
    time.tzset()

    name = os.path.basename(argv[0])[:-3]  # Remove ".py"

    if len(argv) > 1:
        configFile = os.path.realpath(argv[1])
    else:
        configFile = 'config.ini'

    run(name, configFile)


if __name__ == '__main__':
    main(sys.argv)
