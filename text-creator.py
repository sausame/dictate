#!/usr/bin/env python
# -*- coding:utf-8 -*-

import csv
import json
import os
import pyperclip
import random
import re
import sys
import time
import traceback

from datetime import datetime
from difflib import SequenceMatcher
from synonym import SynonymBook
from utils import notify, reprDict, getch, getchar, getProperty, prGreen, prRed, prYellow, prLightPurple, prPurple, prCyan, prLightGray, prBlack, stdinReadline


class TextCreator:

    def __init__(self, dirname):

        self.dirname = dirname

        self.chapterNumber = 1
        self.pageNumber = 1

        self.load()

    def load(self):

        book = SynonymBook(self.dirname)
        if not book.load():
            return

        self.chapterNumber = book.chapters[len(book.chapters) - 1] + 1
        self.pageNumber = 1

    def getPathname(self):
        pathname = 'unit-b{}-{}.txt'.format(self.chapterNumber,
                                            self.pageNumber)
        return os.path.join(self.dirname, pathname)

    def increase(self):
        self.chapterNumber += 1
        self.pageNumber = 1

    def save(self, parts):

        pathname = self.getPathname()

        with open(pathname, 'w+', newline='') as fp:
            for index in range(len(parts)):
                if index > 0:
                    fp.write('\n\n\n')

                part = re.sub(r'\n+', '\n', parts[index])
                fp.write(part)

        prRed('Saved into {}.'.format(self.getPathname()))

    def sendNotification(self, message):

        notify(title='Chapter {}'.format(self.chapterNumber),
               subtitle='Page {}'.format(self.pageNumber),
               message=message)

    def run(self):

        def isNew(lastSource, source):

            lastLen = len(lastSource)
            length = len(source)

            if lastLen == 0:
                return True

            _, _, size = SequenceMatcher(
                None, lastSource, source).find_longest_match(0, lastLen, 0, length)

            if size * 2 > max(lastLen, length):
                return False

            return True

        def update(parts, source):

            updated = False
            updatedIndex = -1  # For debug

            for index in range(len(parts)):
                part = parts[index]

                if not isNew(part, source):
                    if parts[index] != source:
                        parts[index] = source
                        updatedIndex = index

                    updated = True
                    break
            else:
                for index in range(len(parts)):
                    part = parts[index]

                    if len(part) == 0:
                        parts[index] = source
                        updated = True

                        updatedIndex = index
                        break

            if updatedIndex == 0:
                prLightGray(source)
                self.sendNotification(source)
            elif updatedIndex == 1:
                prPurple(source)
                self.sendNotification(source)

            return updated, updatedIndex

        parts = [''] * 2

        os.system('clear')

        self.sendNotification('Filling texts ...')
        prCyan('Filling texts for chapter {} and page {}.'.format(
            self.chapterNumber, self.pageNumber))

        pyperclip.copy('')

        while True:

            source = pyperclip.paste()
            if not source:
                time.sleep(1)
                continue

            updated, updatedIndex = update(parts, source)

            if updated:

                if len(parts[0]) == 0 or len(parts[1]) == 0:
                    time.sleep(1)
                    continue

                if updatedIndex >= 0:
                    self.sendNotification('Save ?')
                    prCyan('Save page {} of chapter {}?'.format(
                        self.pageNumber, self.chapterNumber))

                _, timeout = stdinReadline(2)
                if timeout:
                    continue

                pyperclip.copy('')

            self.save(parts)
            parts = [''] * 2

            self.sendNotification('Increase chapter ?')
            prCyan('Increase chapter number {} -> {}?'.format(self.chapterNumber,
                   self.chapterNumber + 1))

            _, timeout = stdinReadline(3)
            if not timeout:
                self.increase()
            else:
                self.pageNumber += 1

            os.system('clear')

            self.sendNotification('Filling texts ...')
            prCyan('Filling texts for chapter {} and page {}.'.format(
                self.chapterNumber, self.pageNumber))


def run(name, configFile):

    try:
        prGreen('Now: {}'.format(datetime.now().strftime('%Y-%m-%d %H:%M:%S')))

        synonymPath = getProperty(configFile, 'synonym-path')

        creator = TextCreator(synonymPath)
        creator.run()

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
