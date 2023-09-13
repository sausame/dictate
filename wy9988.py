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

    def __init__(self):
        with open('templates/phrases.txt') as fp:
            lines = fp.read().splitlines()

        if len(lines) == 0:
            return

        self.reagents1 = []
        self.reagents2 = []

        self.phrases = []

        for line in lines:
            parts = line.split(' ')

            self.reagents1.append(parts[0])
            self.reagents2.append('{}.'.format(parts[0]))
            self.phrases.append(parts[1])

    def find(self, src):
        for index in range(len(self.reagents1)):
            if src == self.reagents1[index]:
                return index

        for index in range(len(self.reagents2)):
            if src == self.reagents2[index]:
                return index

        return -1

    def matches(self, src):

        if not src:
            return False

        texts = src.split('/')
        if len(texts) == 0:
            return False

        for text in texts:

            text = text.strip()
            if len(text) == 0:
                continue

            pos = self.find(text)
            if pos < 0:
                return False

        return True

    def get(self, src):

        if not src:
            return None

        texts = src.split('/')
        phrases = []

        for text in texts:

            text = text.strip()
            if len(text) == 0:
                continue

            pos = self.find(text)
            if pos < 0:
                return None

            phrases.append(self.phrases[pos])

        if len(phrases) == 0:
            return None

        return '/'.join(phrases)

    def appendToList(self, alist, content):

        text = self.get(content)

        if text:
            alist.append(text)
        else:
            alist.append(content)


class Explanation:

    @staticmethod
    def get(phrase, explanation):

        parts = []

        flag = False
        start = 0

        for pos in range(len(explanation)):
            word = explanation[pos]

            if not flag:
                if ord(word) >= 0x1000:
                    flag = True
                    if pos > start:
                        content = explanation[start:pos].strip()
                        phrase.appendToList(parts, content)

                    start = pos
                else:
                    continue
            else:
                if ord(word) >= 0x1000:
                    continue
                else:
                    flag = False
                    if pos > start:
                        parts.append(explanation[start:pos].strip())
                    start = pos
        else:
            content = explanation[start:].strip()
            if flag:
                parts.append(content)
            else:
                phrase.appendToList(parts, content)

        return ' '.join(parts)


class SynonymPage:

    def __init__(self, phrase):
        self.phrase = phrase

    def parse(self, pathname):

        prGreen('Parsing {} ...'.format(pathname))

        lines = []

        with open(pathname) as fp:
            lines = fp.read().splitlines()

            if len(lines) == 0:
                return False

        lane1 = []
        lane2 = []
        curLane = lane1

        count = 0

        for line in lines:

            line = line.strip()

            if len(line) <= 1:
                count += 1
                continue

            if count >= 3:
                curLane = lane2

            self.append(curLane, line)

        return self.save(pathname, lane1, lane2)

    def append(self, lane, line):

        def appendContent(segments, content):
            self.phrase.appendToList(segments, content)

        def appendText(lane, line):

            if not re.search(r'[a-zA-Z]+', line):
                pos = len(lane) - 1
                if pos < 0:
                    raise Exception('Error:{}'.format(line))

                lane[pos] += line
                return

            segments = line.split(' ')
            newSegments = []

            position = -1

            for segment in segments:
                if len(segment) == 0:
                    continue

                if position >= 0:
                    appendContent(newSegments, segment)
                    continue

                for pos in range(len(segment)):
                    code = segment[pos]

                    if ord(code) >= 0x1000:
                        if pos > 0:
                            appendContent(newSegments, segment[:pos])

                        position = len(newSegments)

                        appendContent(newSegments, segment[pos:])
                        break
                else:
                    appendContent(newSegments, segment)

            for pos in range(position - 1, -1, -1):

                segment = newSegments[pos]
                if self.phrase.matches(segment):
                    continue

                position = pos + 1
                break

            if position <= 0:
                string = ' '.join(newSegments)
                lane.append(string.strip())
                return

            string = ' '.join(newSegments[:position])
            lane.append(string.strip())

            string = ' '.join(newSegments[position:])
            string = Explanation.get(self.phrase, string)
            lane.append(string.strip())

        lineType = len(lane) % 2
        if 0 == lineType:
            appendText(lane, line)
            return

        string = Explanation.get(self.phrase, line)
        lane.append(string)

    def save(self, pathname, lane1, lane2):

        pos = pathname.rfind('.')
        prefix = pathname[:pos]

        len1 = len(lane1)
        len2 = len(lane2)

        if len1 == len2 and len1 % 2 == 0:
            succeeded = True
            filename = '{}.csv'.format(prefix)
        else:
            succeeded = False
            filename = '{}.error.csv'.format(prefix)

        try:
            with open(filename, 'w+', newline='') as fp:
                writer = csv.writer(fp, delimiter='\t')

                '''
                HEADERS = ['Expression 1', 'Explanation 1', 'Expression 2', 'Explanation 2']
                writer.writerow(HEADERS)
                '''

                index = 0

                while index * 2 < len1 or index * 2 < len2:
                    pos = index * 2
                    index += 1

                    values = [''] * 4

                    for i in range(2):
                        pos += i

                        if pos < len1:
                            values[i] = lane1[pos]

                        if pos < len2:
                            values[2 + i] = lane2[pos]

                    writer.writerow(values)

                if succeeded:
                    prGreen('Successfully saved into {}'.format(filename))
                else:
                    prRed('Failed and saved into {}'.format(filename))

                return succeeded

        except Exception as e:
            remove(filename)

            prRed('Error occurs at {}'.format(
                datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
            traceback.print_exc(file=sys.stdout)

        return False


class SynonymDictionary:

    def __init__(self, dirname):

        self.dirname = dirname

        self.dictpath = os.path.join(dirname, 'dictionary.json')

        self.dictionary = dict()
        self.phrase = Phrase()

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

    def isParsed(self, pathname):

        key = self.getkey(pathname)
        if key not in self.dictionary.keys():
            return False

        value = int(os.path.getmtime(pathname))
        if value != self.dictionary[key]:
            return False

        csvPathname = '{}.csv'.format(pathname[:-4])
        return os.path.exists(csvPathname)

    def update(self, pathname):
        key = self.getkey(pathname)
        value = int(os.path.getmtime(pathname))

        self.dictionary[key] = value

    def parse(self):

        pathnames = getPathnames(self.dirname, '.txt')

        num = len(pathnames)
        if num == 0:
            prRed('No file is found in {}'.format(self.dirname))
            return

        phrase = Phrase()
        page = SynonymPage(phrase)

        succeededCount = 0
        failedCount = 0
        skippedCount = 0

        for pathname in pathnames:
            if self.isParsed(pathname):
                skippedCount += 1
                continue

            if page.parse(pathname):
                self.update(pathname)
                succeededCount += 1
            else:
                failedCount += 1

        prGreen('Parsed {}, failed {}, skipped {}'.format(
            succeededCount, failedCount, skippedCount))


def run(name, configFile):

    try:
        prGreen('Now: {}'.format(datetime.now().strftime('%Y-%m-%d %H:%M:%S')))

        synonymPath = getProperty(configFile, 'synonym-path')

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
