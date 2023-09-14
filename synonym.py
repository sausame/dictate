#!/usr/bin/env python
# -*- coding:utf-8 -*-

import csv
import os
import random
import re
import sys
import time
import traceback

from datetime import datetime
from tts import LocalTts as Tts
from utils import getch, getchar, getPathnames, getProperty, reprDict, prGreen, prRed, prYellow, prLightPurple, prPurple, prCyan, prLightGray, prBlack, stdinReadline


class Synonym:

    def __init__(self, tts):
        self.tts = tts

    def study(self, values):

        prYellow(''.join(['-'] * 100))

        first = random.randint(0, 1) * 2
        second = 2 - first

        content = '{:^40}\t{:^40}'.format(values[first], values[second])
        prLightGray(content)

        content = '{:^40}\t{:^40}'.format(
            values[first + 1], values[second + 1])
        prPurple(content)

        word = '{},{}'.format(values[first], values[second])
        self.tts.say(word)

        _, timeout = getch(1, isPrompt=False)
        if timeout:
            return False

        prRed('Skip {}'.format(word))
        return True

    def test(self):
        pass


class SynonymChapter:

    def __init__(self):
        self.tts = Tts()
        self.tts.setLanguage('english')

    def study(self, pathname):

        rows = []

        with open(pathname, newline='') as csvfile:
            reader = csv.reader(csvfile, delimiter='\t')

            for row in reader:
                rows.append(row)

        if len(rows) == 0:
            return

        self.studyRows(rows)

    def studyRows(self, rows):

        synonym = Synonym(self.tts)

        random.seed()

        prRed('Notice: press return key to skip one word')

        while len(rows) > 0:

            size = len(rows)

            os.system('clear')

            prYellow(''.join(['='] * 100))
            prYellow('{} synonymes are left.'.format(size))

            indexes = [False] * size
            skipedIndexes = []

            while True:
                index = 0

                pos = random.randint(0, size - 1)

                for offset in range(size):
                    index = (pos + offset) % size
                    if not indexes[index]:
                        indexes[index] = True
                        break
                else:
                    break  # Not found

                skiped = synonym.study(rows[index])
                if skiped:
                    skipedIndexes.append(index)

            if len(skipedIndexes) == 0:
                continue

            skipedIndexes = sorted(skipedIndexes, reverse=True)
            for index in skipedIndexes:
                rows.pop(index)

    def test(self):
        pass


class SynonymBook:

    def __init__(self, bookDir):

        self.bookDir = bookDir

        self.chapters = []
        self.chapterDict = dict()

    def extend(self, pathname):

        def getNumbers(src):

            numbers = []

            REGEX = r'(\d+)-(\d+)'
            matches = re.finditer(REGEX, src, re.MULTILINE)

            for matchNum, match in enumerate(matches, start=1):
                for groupNum in range(0, len(match.groups())):
                    groupNum = groupNum + 1
                    numbers.append(int(match.group(groupNum)))

            return numbers

        numbers = getNumbers(pathname)

        chapterNumber = numbers[0]
        pageNumber = numbers[1]

        if chapterNumber not in self.chapters:
            self.chapters.append(chapterNumber)
            self.chapters = sorted(self.chapters)

        chapterKey = 'chapter-{}'.format(chapterNumber)

        if chapterKey in self.chapterDict.keys():
            chapter = self.chapterDict[chapterKey]
        else:
            chapter = dict()
            chapter['pages'] = []

        chapter['pages'].append(pageNumber)
        chapter['pages'] = sorted(chapter['pages'])

        pageKey = 'page-{}'.format(pageNumber)
        chapter[pageKey] = pathname

        self.chapterDict[chapterKey] = chapter

    def load(self):

        pathnames = getPathnames(self.bookDir, '.csv')

        num = len(pathnames)
        if num == 0:
            prRed('No file is found in {}'.format(self.bookDir))
            return False

        for pathname in pathnames:
            self.extend(pathname)

        return True

    def study(self):

        def readNumber(array, promptPrefix, timeout):

            start = array[0]
            end = array[len(array) - 1]

            while True:
                prCyan('{} from {} to {}, press return to select one randomly:'.format(
                    promptPrefix, start, end))

                number = stdinReadline(timeout, isPrompt=False)

                try:
                    if len(number) > 0:
                        number = int(number)
                        if number not in array:
                            prRed(
                                'No NO.{}, please choose another one'.format(number))
                            continue

                        return number
                except ValueError as e:
                    pass

                index = random.randint(0, len(array) - 1)
                return array[index]

        try:
            os.system('clear')

            print('Now: ', datetime.now().strftime('%Y-%m-%d %H:%M:%S'))

            if not self.load():
                return

            random.seed()

            chapterNumber = readNumber(
                self.chapters, 'Please select a chapter', 10)
            prYellow('Chapter "{}" is selected.'.format(chapterNumber))

            chapterKey = 'chapter-{}'.format(chapterNumber)
            pageNumber = readNumber(
                self.chapterDict[chapterKey]['pages'], 'Please select a page', 10)
            prYellow('Page "{}" is selected.'.format(pageNumber))

            pageKey = 'page-{}'.format(pageNumber)
            pathname = self.chapterDict[chapterKey][pageKey]
            prYellow('File "{}" is selected.'.format(pathname))

            chapter = SynonymChapter()
            chapter.study(pathname)

        except KeyboardInterrupt:
            pass
        except Exception as e:
            prRed('Error occurs at {}'.format(
                datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
            traceback.print_exc(file=sys.stdout)
        finally:
            pass


def run(name, configFile):

    synonymPath = getProperty(configFile, 'synonym-path')

    book = SynonymBook(synonymPath)
    book.study()


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
