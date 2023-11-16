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
from phrase import SentenceGroup
from tts import LocalTts as Tts
from utils import getMd5, getFileMd5, remove, reprDict, runCommand, getch, getchar, getPathnames, getProperty, prGreen, prRed, prYellow, prLightPurple, prPurple, prCyan, prLightGray, prBlack, stdinReadline


class SynonymPage(SentenceGroup):

    def read(self, pathname, info=None):

        prGreen('Parsing {} ...'.format(pathname))

        super().read(pathname)

        return self.save(pathname, info)

    def refine(self, pathname, info):

        content = ''
        size = len(self.group)
        mid = int(size / 2) - 1
        for index in range(size):
            content += self.group[index] + '\n'

            if index == mid:
                content += '\n\n\n'

        if info and info['md5code'] == getMd5(content):
            return False

        with open(pathname, 'w+', newline='') as fp:
            fp.write(content)
            prGreen('Refined {}'.format(pathname))

            return True

        return False

    def saveAsSynonym(self, pathname):

        pos = pathname.rfind('.')
        prefix = pathname[:pos]

        errorFilename = '{}.error.csv'.format(prefix)
        succeededFilename = '{}.csv'.format(prefix)

        size = int(len(self.group) / 4)
        if len(self.group) % 4 == 0:
            succeeded = True
            filename = succeededFilename

            remove(errorFilename)
        else:
            succeeded = False
            filename = errorFilename

        try:
            with open(filename, 'w+', newline='') as fp:
                writer = csv.writer(fp, delimiter='\t')

                '''
                HEADERS = ['Expression 1', 'Explanation 1', 'Expression 2', 'Explanation 2']
                writer.writerow(HEADERS)
                '''

                index = 0

                for index in range(size):

                    firstPos = index * 2
                    secondPos = firstPos + size * 2

                    values = [self.group[firstPos],
                              self.group[firstPos + 1],
                              self.group[secondPos],
                              self.group[secondPos + 1]]

                    # writer.writerow(values)

                    writer.writerow(['{:^40}'.format(self.group[firstPos]),
                                     self.group[firstPos + 1]])
                    writer.writerow(['{:^40}'.format(self.group[secondPos]),
                                     self.group[secondPos + 1]])
                    # writer.writerow(['', ''])

                if succeeded:
                    prGreen('Successfully saved into {}'.format(filename))

                else:
                    values = []
                    for index in range(size * 4, len(self.group)):
                        values.append(self.group[index])
                    writer.writerow(values)

                    print(len(self.group), reprDict(self.group))

                    prRed('Failed and saved into {}'.format(filename))

                return succeeded

        except Exception as e:
            remove(filename)

            prRed('Error occurs at {}'.format(
                datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
            traceback.print_exc(file=sys.stdout)

        return False

    def save(self, pathname, info):
        self.refine(pathname, info)
        return self.saveAsSynonym(pathname)


class SynonymDictionary:

    def __init__(self, dirname):

        self.dirname = dirname

        self.dictpath = os.path.join(dirname, 'dictionary.json')

        self.dictionary = dict()

        self.load()

    def __del__(self):
        self.save()

    def load(self):

        if not os.path.exists(self.dictpath):
            return

        with open(self.dictpath) as fp:
            content = json.loads(fp.read())
            self.dictionary.update(content)

    def save(self):
        with open(self.dictpath, 'w+', newline='') as fp:
            fp.write(reprDict(self.dictionary))

    def getkey(self, pathname):
        return pathname.replace('/', '-').replace('\\', '-').replace('.', '-')

    def getInfo(self, pathname):
        key = self.getkey(pathname)
        if key not in self.dictionary.keys():
            return None

        return self.dictionary[key]

    def isParsed(self, pathname):

        info = self.getInfo(pathname)
        if not info:
            return False

        if info['timestamp'] != int(os.path.getmtime(pathname)):
            return False

        if info['md5code'] != getFileMd5(pathname):
            return False

        csvPathname = '{}.csv'.format(pathname[:-4])
        return os.path.exists(csvPathname)

    def update(self, pathname):
        key = self.getkey(pathname)

        md5code = getFileMd5(pathname)
        timestamp = int(os.path.getmtime(pathname))

        self.dictionary[key] = {
            'timestamp': timestamp,
            'md5code': md5code,
        }

    def parse(self):

        pathnames = getPathnames(self.dirname, '.txt')

        num = len(pathnames)
        if num == 0:
            prRed('No file is found in {}'.format(self.dirname))
            return

        succeededCount = 0
        failedCount = 0
        skippedCount = 0

        page = SynonymPage()

        for pathname in pathnames:
            if self.isParsed(pathname):
                skippedCount += 1
                continue

            info = self.getInfo(pathname)

            if page.read(pathname, info):
                self.update(pathname)
                succeededCount += 1
            else:
                failedCount += 1

        prGreen('Parsed {}, failed {}, skipped {}'.format(
            succeededCount, failedCount, skippedCount))


def run(name, configFile, pathname=None):

    try:
        prGreen('Now: {}'.format(datetime.now().strftime('%Y-%m-%d %H:%M:%S')))

        synonymPath = getProperty(configFile, 'synonym-path')

        if pathname:
            page = SynonymPage()
            page.read(pathname)
        else:
            dictionary = SynonymDictionary(synonymPath)
            dictionary.parse()

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
        print('Usage:\n\t', argv[0], '[PATH-NAME]\n')

    os.environ['TZ'] = 'Asia/Shanghai'
    time.tzset()

    name = os.path.basename(argv[0])[:-3]  # Remove ".py"
    pathname = None

    if len(argv) > 1:
        pathname = os.path.realpath(argv[1])

    run(name, 'config.ini', pathname)


if __name__ == '__main__':
    main(sys.argv)
