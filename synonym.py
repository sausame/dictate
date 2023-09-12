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
from utils import getch, getchar, getPathnames, getProperty, prGreen, prRed, prYellow, prLightPurple, prPurple, prCyan, prLightGray, prBlack, stdinReadline

class Synonym:

    def __init__(self, tts):
        self.tts = tts

    def study(self, values):

        num = int(len(values) / 2)
        for index in range(num):
            pos = index * 2
            prYellow('{}\n\t{}'.format(values[pos], values[pos + 1]))
            self.tts.say(values[pos])

            _, timeout = getch(2, 'Press any key to skip')
            if not timeout:
                prRed('Skip {}'.format('|'.join(values)))
                return True

        return False

    def test(self):
        pass

class SynonymChapter:

    def __init__(self):
        self.tts = Tts()
        self.tts.setLanguage('english')

    def study(self, pathname):

        rows = []

        with open(pathname, newline='') as csvfile:
            reader = csv.reader(csvfile, delimiter='|')

            for row in reader:
                rows.append(row)

        if len(rows) == 0:
            return

        self.studyRows(rows)

    def studyRows(self, rows):

        synonym = Synonym(self.tts)

        random.seed()

        while len(rows) > 0:

            size = len(rows)

            print('---------------------------------------------------------------')
            print(size, 'synonymes are left.')

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
                    break # Not found

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

    def study(self):

        try:
            print('Now: ', datetime.now().strftime('%Y-%m-%d %H:%M:%S'))

            pathnames = getPathnames(self.bookDir, '.csv')

            num = len(pathnames)
            if num == 0:
                prRed('No file is found in {}'.format(self.bookDir))
                return
 
            pathnames = sorted(pathnames, reverse=True)

            sequenceNum = -1
            while sequenceNum < 0 or sequenceNum >= num:

                prGreen('Please select a chapter you want to study:')

                for index in range(num):
                    pathname = pathnames[index]
                    prLightPurple('{:3}\t{}'.format(index+1, pathname))

                prGreen(
                    'Please input the sequence number (default is {}):'.format(num))

                sequenceNum = stdinReadline(20, isPrompt=False)

                try:
                    if len(sequenceNum) > 0:
                        sequenceNum = int(sequenceNum) - 1
                    else:
                        sequenceNum = num - 1
                except ValueError as e:
                    sequenceNum = num - 1

            pathname = pathnames[sequenceNum]
            prYellow('"{}" is selected.'.format(pathname))

            chapter = SynonymChapter()
            chapter.study(pathname)

        except KeyboardInterrupt:
            pass
        except Exception as e:
            prRed('Error occurs at {}'.format(datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
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
