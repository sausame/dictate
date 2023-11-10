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
from utils import getch, getchar, getPathnames, getProperty, reprDict, prGreen, prRed, prYellow, prLightPurple, prPurple, prCyan, prLightGray, prBlack, stdinReadline


class Synonym:

    def __init__(self, tts=None):
        self.tts = tts

    def toDict(self, values, extra=None):

        def buildKey(values):
            regex = re.compile('[^a-zA-Z0-9]')
            word1 = regex.sub('_', values[0].strip())
            word2 = regex.sub('_', values[2].strip())
            return '{}---{}'.format(word1, word2)

        word1 = values[0].strip()
        word2 = values[2].strip()

        if word1 > word2:
            newValues = [
                values[2],
                values[3],
                values[0],
                values[1],
            ]
        else:
            newValues = values

        key = buildKey(newValues)

        result = {
            'word1': newValues[0].strip(),
            'word2': newValues[2].strip(),
            'explanation1': newValues[1].strip(),
            'explanation2': newValues[3].strip()
        }

        if extra:
            result.update(extra)

        return {key: result}

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

    def toDict(self, pathname, extra=None):

        results = dict()

        with open(pathname, newline='') as csvfile:
            reader = csv.reader(csvfile, delimiter='\t')

            extra

            synonym = Synonym()
            for row in reader:
                result = synonym.toDict(row, extra)
                results.update(result)
            
        return results

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

        self.chapterNumbers = []
        self.chapterDict = dict()

    @staticmethod
    def getChapterKey(number):
        return 'chapter-{}'.format(number)

    @staticmethod
    def getPageKey(number):
        return 'page-{}'.format(number)

    def getPages(self, chapterNumber):
        chapterKey = self.getChapterKey(chapterNumber)
        return self.chapterDict[chapterKey]['pages']

    def getPathname(self, chapterNumber, pageNumber):
        chapterKey = self.getChapterKey(chapterNumber)
        pageKey = self.getPageKey(pageNumber)

        return self.chapterDict[chapterKey][pageKey]

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

        if chapterNumber not in self.chapterNumbers:
            self.chapterNumbers.append(chapterNumber)
            self.chapterNumbers = sorted(self.chapterNumbers)

        chapterKey = self.getChapterKey(chapterNumber)

        if chapterKey in self.chapterDict.keys():
            chapter = self.chapterDict[chapterKey]
        else:
            chapter = dict()
            chapter['pages'] = []

        chapter['pages'].append(pageNumber)
        chapter['pages'] = sorted(chapter['pages'])

        pageKey = self.getPageKey(pageNumber)
        chapter[pageKey] = pathname

        self.chapterDict[chapterKey] = chapter

    def load(self, suffix='.csv'):

        pathnames = getPathnames(self.bookDir, suffix)

        num = len(pathnames)
        if num == 0:
            prRed('No file is found in {}'.format(self.bookDir))
            return False

        for pathname in pathnames:
            self.extend(pathname)

        return True

    def loadRaw(self):
        return self.load('.txt')

    def toDict(self):

        if not self.load():
            return None

        wholeResults = dict()
        chapter = SynonymChapter()

        for chapterNumber in self.chapterNumbers:
            pages = self.getPages(chapterNumber)

            for pageNumber in pages:
                pathname = self.getPathname(chapterNumber, pageNumber)

                extra = {
                    'chapter': chapterNumber,
                    'page': pageNumber,
                }

                results = chapter.toDict(pathname, extra)

                wholeResults.update(results)

        return wholeResults

    def saveToFile(self, pathname):

        with open(pathname, 'w+', newline='') as fp:
            result = self.toDict()
            fp.write(reprDict(result))
            prGreen('Save to {}'.format(pathname))

    def study(self):

        def readNumber(array, promptPrefix, timeout):

            start = array[0]
            end = array[len(array) - 1]

            while True:
                prCyan('{} from {} to {}, press return to select one randomly:'.format(
                    promptPrefix, start, end))

                number, _ = stdinReadline(timeout, isPrompt=False)

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

        if not self.load():
            return

        random.seed()

        chapterNumber = readNumber(
            self.chapterNumbers, 'Please select a chapter', 10)
        prYellow('Chapter "{}" is selected.'.format(chapterNumber))

        pages = self.getPages(chapterNumber)
        pageNumber = readNumber(pages, 'Please select a page', 10)
        prYellow('Page "{}" is selected.'.format(pageNumber))

        pathname = self.getPathname(chapterNumber, pageNumber)
        prYellow('File "{}" is selected.'.format(pathname))

        chapter = SynonymChapter()
        chapter.study(pathname)


def run(name, configFile, pathname):

    synonymPath = getProperty(configFile, 'synonym-path')

    try:
        book = SynonymBook(synonymPath)

        if pathname:
            book.saveToFile(pathname)
        else:
            os.system('clear')
            print('Now: ', datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
            book.study()

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
        print('Usage:\n\t', argv[0], '[SAVE-PATH-NAME]\n')

    os.environ['TZ'] = 'Asia/Shanghai'
    time.tzset()

    name = os.path.basename(argv[0])[:-3]  # Remove ".py"

    if len(argv) > 1:
        pathname = os.path.realpath(argv[1])
    else:
        pathname = None

    run(name, 'config.ini', pathname)


if __name__ == '__main__':
    main(sys.argv)
