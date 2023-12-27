#!/usr/bin/env python
# -*- coding:utf-8 -*-

import os
import re
import sys
import time
import traceback

from datetime import datetime
from tts import LocalTts as Tts
from utils import remove, reprDict, runCommand, getch, getchar, getPathnames, getProperty, prGreen, prRed, prYellow, prLightPurple, prPurple, prCyan, prLightGray, prBlack, stdinReadline

def getNumbers(pathname):

    numbers = []

    REGEX = r'(\d+)-(\d+)'
    matches = re.finditer(REGEX, pathname, re.MULTILINE)

    for matchNum, match in enumerate(matches, start=1):
        for groupNum in range(0, len(match.groups())):
            groupNum = groupNum + 1
            numbers.append(int(match.group(groupNum)))

    return numbers

class BaseExpression:

    REPLACE_EXPRESSION_DICT = {
        'en-multiple-dot': {
            'regex': r'[a-zA-Z0-9\']+([ \t]*\.\.[.]*[ \t]*)',
            'exp': ' ... ',
            'conflict': 'multiple-dot', # TODO: not good
        },
        'multiple-dot': {
            'regex': r'([ \t]*\.\.[.]*[ \t]*)',
            'exp': '...',
            'conflict': 'en-multiple-dot', # TODO: not good
        },
    }

    EXPRESSION_DICT = {
        'single-dot': {
            'regex': r'([·]+)',
            'exp': '.'
        },
        'comma': {
            'regex': r'([，]+)',
            'exp': ','
        },
        'blank': {
            'regex': r'([ ]+)',
            'exp': ' '
        },
        'parenthesis': {
            'regex': r'\(([^\)]+)$',
            'exp': '({})',
            'strip': True,
        },
        'parenthesis-2': {
            'regex': r'\(([^\)]+)\)',
            'exp': '({})',
            'strip': True,
        },
        'square-brackets': {
            'regex': r'\[([^\]]+)$',
            'exp': '[{}]',
            'strip': True,
        },
        'square-brackets-2': {
            'regex': r'\[([^\]]+)\]',
            'exp': '[{}]',
            'strip': True,
        },
    }

    # Return a list of positions
    @staticmethod
    def find(string, regex):

        positions = []

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
    def findall(string, expressionDict):
        # Add a blank in front of the line
        string = ' ' + string

        allPositions = []

        for key in expressionDict.keys():
            expression = expressionDict[key]

            positions = BaseExpression.find(string, expression['regex'])
            if not positions:
                continue

            for start, end in positions:
                allPositions.append((start - 1, end - 1))

        if len(allPositions) == 0:
            return None

        return sorted(allPositions)

    @staticmethod
    def replaceall(string, expressionDict):

        dest = string

        conflicts = dict()

        for key in expressionDict.keys():
            expression = expressionDict[key]

            positions = BaseExpression.find(dest, expression['regex'])
            if not positions:
                continue

            if 'conflict' in expression.keys() and expression['conflict'] in conflicts.keys():
                continue

            conflicts[key] = positions

            lastEnd = 0
            temp = ''

            for start, end in positions:
                temp += dest[lastEnd:start] + expression['exp']
                lastEnd = end
            else:
                temp += dest[lastEnd:]

            dest = temp

        return dest

    @staticmethod
    def refine(string, expression):

        regex = expression['regex']
        exp = expression['exp']

        dest = None
        lastEnd = 0

        matches = re.finditer(regex, string, re.MULTILINE)
        for matchNum, match in enumerate(matches, start=1):
            groupNum = len(match.groups()) 

            if groupNum == 0:
                continue

            if groupNum > 1:
                raise TypeError('No implement for {} groups'.format(groupNum))

            if not dest:
                dest = ''
            
            content = match.group(1)
            if 'strip' in expression.keys():
                content = content.strip()

            content = exp.format(content)

            dest += string[lastEnd:match.start()] + content
            lastEnd = match.end()

        if dest:
            dest += string[lastEnd:]
            return dest

        return string

    @staticmethod
    def refineall(string, expressionDict):

        dest = string

        conflicts = dict()

        for key in expressionDict.keys():
            expression = expressionDict[key]

            if 'conflict' in expression.keys() and expression['conflict'] in conflicts.keys():
                continue

            conflicts[key] = True

            dest = BaseExpression.refine(dest, expression)

        return dest

    @staticmethod
    def replaceallWithBaseExpression(string):

        dest = BaseExpression.replaceall(string, BaseExpression.REPLACE_EXPRESSION_DICT)
        dest = BaseExpression.refineall(dest, BaseExpression.EXPRESSION_DICT)

        return dest

class Category:

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
    ABBR_REGEX = r'[ \t](abbr[,\.]*)[^a-zA-Z]+'
    AUX_REGEX = r'[ \t](aux[,\.]*)[^a-zA-Z]+'
    NUM_REGEX = r'[ \t](num[,\.]*)[^a-zA-Z]+'
    ART_REGEX = r'[ \t](art[,\.]+)[^a-zA-Z]+'

    CATEGORY_DICT = {
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
        },
        'abbr': {
            'regex': ABBR_REGEX,
            'exp': 'abbr.'
        },
        'aux': {
            'regex': AUX_REGEX,
            'exp': 'aux.'
        },
        'num': {
            'regex': NUM_REGEX,
            'exp': 'num.'
        },
        'art': {
            'regex': ART_REGEX,
            'exp': 'art.'
        },
    }

    @staticmethod
    def findall(string):
        return BaseExpression.findall(string, Category.CATEGORY_DICT)

    @staticmethod
    def replaceall(string):

        # Add blanks in front of and end of the line
        dest = ' ' + string + ' '
        dest = BaseExpression.replaceall(dest, Category.CATEGORY_DICT)
        dest = dest[1:-1]  # remove the blanks

        dest = BaseExpression.replaceallWithBaseExpression(dest)

        return dest


class Phrase:

    REGEXES = [r"\([a-zA-Z0-9']+\.*\)",
               r"[a-zA-Z0-9']+",
               r'[ ,\.%$\-]+']

    @staticmethod
    def find(string):
        lanes = Phrase.multiFindAll(Phrase.REGEXES, string)
        return Phrase.findContinuousRange(lanes)

    @staticmethod
    def findall(regex, string):
        positions = []

        matches = re.finditer(regex, string, re.MULTILINE)

        for matchNum, match in enumerate(matches, start=1):
            positions.append((match.start(), match.end()))

        return positions

    @staticmethod
    def multiFindAll(regexes, string):
        lanes = []

        for regex in regexes:
            positions = Phrase.findall(regex, string)

            if len(positions) == 0:
                continue

            lanes.append(positions)

        if len(lanes) == 0:
            return None

        return lanes

    @staticmethod
    def findContinuousRange(lanes):

        if not lanes:
            return 0, 0

        lane = 0

        minPosition = -1
        maxPosition = 0

        for index in range(0, len(lanes)):
            positions = lanes[index]
            start, end = positions[0]

            if minPosition < 0 or start < minPosition:
                lane = index

                minPosition = start
                maxPosition = end

        indexes = [0] * len(lanes)

        isContinued = True

        while isContinued:

            isContinued = False

            for index in range(0, len(lanes)):

                if index == lane:
                    continue

                positions = lanes[index]
                length = len(positions)

                curIndex = indexes[index]
                if curIndex == length:
                    continue

                while curIndex < length:
                    start, end = positions[curIndex]

                    if start > maxPosition or end > maxPosition:
                        break

                    curIndex += 1

                indexes[index] = curIndex
                if curIndex == length:
                    # not found
                    continue

                start, end = positions[curIndex]

                if start <= maxPosition and end > maxPosition:
                    isContinued = True

                    maxPosition = end
                    lane = index

        return minPosition, maxPosition


class Explanation:

    EXCLUDE_REGEX = r"([^a-zA-Z0-9 .%$\-'])"
    INCLUDE_REGEX = r'[a-zA-Z0-9]'


    # Find the first one
    @staticmethod
    def find(string):

        start, end = Phrase.find(string)

        if start > 0:
            return 0

        if end == 0 or end < len(string):
            return end

        return -1

    @staticmethod
    def findold(string):

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

        dest = Category.replaceall(src)
        sentence = {
            'exist-explanation': True,
            'changed': dest != src,
            'group': [dest]
        }

        positions = Category.findall(dest)

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
            length = len(group)

            if length == 0 or length % 2 == 1:
                return False

            if not sentence['exist-explanation']:
                return False

            if len(sentence['group']) > 1:
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
