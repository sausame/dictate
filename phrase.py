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
    CONJ_REGEX = r'[ \t](conj[,\.]*)[^a-zA-Z]+'
    PRON_REGEX = r'[ \t](pron[,\.]*)[^a-zA-Z]+'
    DEB_REGEX = r'[ \t](deb[,\.]*)[^a-zA-Z]+'

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
        },
        'conj': {
            'regex': CONJ_REGEX,
            'exp': 'conj.'
        },
        'pron': {
            'regex': PRON_REGEX,
            'exp': 'pron.'
        },
        'deb': {
            'regex': DEB_REGEX,
            'exp': 'deb.'
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

    EXCLUDE_REGEX = r"([^a-zA-Z0-9 .%$\-'])"
    INCLUDE_REGEX = r'[a-zA-Z0-9]'

    # Find the first one
    @staticmethod
    def find(string):

        matches = re.finditer(Explanation.EXCLUDE_REGEX, string, re.MULTILINE)

        for matchNum, match in enumerate(matches, start=1):

            for groupNum in range(0, len(match.groups())):
                groupNum = groupNum + 1

                start = match.start(groupNum)

                if re.search(Explanation.INCLUDE_REGEX, string[:start], re.MULTILINE):
                    return start

                # Not found
                return 0

        return -1


class Sentence:

    # Find the first one
    @staticmethod
    def refine(src):

        if len(src) == 0:
            return None

        dest = Phrase.replaceall(src)
        sentence = {
            'exist-explanation': True,
            'changed': dest != src,
            'group': [dest]
        }

        positions = Phrase.findall(dest)

        if positions is not None:
            start, end = positions[0]
            if start == 0:
                return sentence

            sentence['changed'] = True
            sentence['group'] = [dest[:start], dest[start:]]
            return sentence

        position = Explanation.find(dest)
        if position == 0:
            return sentence

        if position > 0:
            sentence['changed'] = True
            sentence['group'] = [dest[:position], dest[position:]]
            return sentence

        sentence['exist-explanation'] = False
        return sentence


class SentenceGroup:

    def reset(self):
        self.group = []

    def read(self, pathname):

        self.reset()

        with open(pathname) as fp:
            lines = fp.read().splitlines()

            for line in lines:
                sentence = Sentence.refine(line)
                if not sentence:
                    continue

                self.extend(sentence)

        return self.group

    def extend(self, sentence):

        def shouldExtendExplanation(sentence, group):
            if not sentence['exist-explanation']:
                return False

            if len(sentence['group']) > 1:
                return False

            if len(group) % 2 == 1:
                return False

            return True

        def shouldCombine(sentence, group):
            if len(group) % 2 == 0:
                return False

            if len(sentence['group']) < 2:
                return False

            return True

        if shouldExtendExplanation(sentence, self.group):
            self.group[len(self.group) - 1] += sentence['group'][0]
            return

        if shouldCombine(sentence, self.group):
            self.group.append(''.join(sentence['group']))
            return

        self.group.extend(sentence['group'])

    def test(self, pathname):

        prBlack('Refining {}'.format(pathname))

        with open(pathname) as fp:
            lines = fp.read().splitlines()

            for line in lines:
                sentence = Sentence.refine(line)
                if not sentence:
                    continue

                if sentence['changed']:
                    prCyan('{}'.format(line))
                    group = sentence['group']
                    if len(group) == 1:
                        prRed('\t{}'.format(group[0]))
                    else:
                        prRed('\t{:40}\t{:40}'.format(group[0], group[1]))
                else:
                    prGreen('{}'.format(line))


def run(name, pathname):

    try:
        prBlack('Now: {}'.format(datetime.now().strftime('%Y-%m-%d %H:%M:%S')))

        group = SentenceGroup()
        group.test(pathname)

        prBlack('{}'.format(''.join(['-'] * 60)))

        sentences = group.read(pathname)
        for index in range(int(len(sentences) / 2)):
            pos = index * 2
            prCyan('{:40}\t{:40}'.format(sentences[pos], sentences[pos + 1]))

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
        print('Usage:\n\t', argv[0], 'PATH-NAME\n')
        return

    os.environ['TZ'] = 'Asia/Shanghai'
    time.tzset()

    name = os.path.basename(argv[0])[:-3]  # Remove ".py"
    pathname = os.path.realpath(argv[1])

    run(name, pathname)


if __name__ == '__main__':
    main(sys.argv)
