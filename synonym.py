#!/usr/bin/env python
# -*- coding:utf-8 -*-

import os
import random
import re
import sys
import time

from datetime import datetime
from tts import LocalTts as Tts
from utils import getchar, getPathnames, prGreen, prYellow, prLightPurple, prPurple, prCyan, prLightGray, prBlack, stdinReadline

class Synonym:

    def __init__(self, tts):
        self.tts = tts

    def studyLine(self, line):
        words = re.split(r'[\t ]+', line.strip())
        return self.study(words)

    def study(self, words):

        for word in words:
            self.tts.say(word)

            timeout = getchar(1, '{}, press any key to skip'.format(word))
            if not timeout:
                return True

        return False

    def test(self):
        pass

class SynonymChapter:

    def __init__(self):
        self.tts = Tts()
        self.tts.setLanguage('english')

    def study(self, pathname):

        with open(pathname) as fp:
            lines = fp.read().splitlines()

        if len(lines) == 0:
            return

        synonym = Synonym(self.tts)

        for line in lines:
            synonym.studyLine(line)

        wholeContents = copy.deepcopy(self.contents)

        while len(lines) > 0:

            size = len(lines)

            print('---------------------------------------------------------------')
            print(size, 'synonym are left.')

            indexes = [False] * size
            studiedIndexes = []

            while True:
                index = 0

                pos = random.randint(0, size)

                for offset in range(size):
                    index = (pos + offset) % size
                    if not indexes[pos]:
                        break
                else:
                    break # Not found

                line = lines[index]

                studied = synonym.studyLine(line)

                if studied:
                    studiedIndexes.append(index)

            if len(studiedIndexes) == 0:
                continue

            studiedIndexes = sorted(studiedIndexes, reverse=True)
            for index in studiedIndexes:
                lines.pop(index)

    def test(self):
        pass


class SynonymBook:

    def __init__(self, bookDir):
        self.bookDir = bookDir

    def study(self):

        try:
            print('Now: ', datetime.now().strftime('%Y-%m-%d %H:%M:%S'))

            pathnames = getPathnames(self.bookDir, '.json')
            pathnames = sorted(pathnames, reverse=True)

            num = len(pathnames)
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
            print('Error occurs at', datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
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
        exit()

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
