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
    
    def get(self, src):

        pos = self.find(src)
        if pos < 0:
            return src

        return self.phrases[pos]

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
                        content = phrase.get(explanation[start:pos].strip())
                        parts.append(content)
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
                content = phrase.get(content)
                parts.append(content)
        
        return ' '.join(parts)

class SynonymPage:

    def __init__(self, phrase):
        self.phrase = phrase

    def parse(self, pathname):

        prRed('Parsing {} ...'.format(pathname))

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
            segments.append(self.phrase.get(content))

        def appendText(lane, line):

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

            for pos in range(position, 0, -1):

                segment = newSegments[pos]
                if self.phrase.find(segment) < 0:
                    continue

                position = pos
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

        if len1 != len2 and len1 % 2 != 0:

            errorfile = '{}-error'.format(prefix)
            with open(errorfile, 'w+') as fp:
                for line in lane1:
                    fp.write(line)

                fp.write('--------------------------------')

                for line in lane2:
                    fp.write(line)

            prRed('Error is found in {} and saved into {}'.format(pathname, errorfile))
            return False

        filename = '{}.csv'.format(prefix)
        with open(filename, 'w+', newline='') as fp:
            writer = csv.writer(fp, delimiter='|')

            '''
            HEADERS = ['Expression 1', 'Explanation 1', 'Expression 2', 'Explanation 2']
            writer.writerow(HEADERS)
            '''

            for index in range(int(len1 / 2)):
                pos = index * 2
                writer.writerow([lane1[pos], lane1[pos + 1], lane2[pos], lane2[pos + 1]])

            prGreen('Successfully saved into {}'.format(filename))

        return True

def run(name, configFile):

    def existCsv(txtPathname):
        csvPathname = '{}.csv'.format(txtPathname[:-4])
        return os.path.exists(csvPathname)

    try:
        print('Now: ', datetime.now().strftime('%Y-%m-%d %H:%M:%S'))

        synonymPath = getProperty(configFile, 'synonym-path')
        pathnames = getPathnames(synonymPath, '.txt')

        num = len(pathnames)
        if num == 0:
            prRed('No file is found in {}'.format(self.bookDir))
            return

        phrase = Phrase()
        page = SynonymPage(phrase)

        succeededCount = 0
        failedCount = 0
        skippedCount = 0

        for pathname in pathnames:
            if existCsv(pathname):
                skippedCount += 1
                continue

            if page.parse(pathname):
                succeededCount += 1
            else:
                failedCount += 1

        prGreen('Parsed {}, failed {}, skipped {}'.format(succeededCount, failedCount, skippedCount))

    except KeyboardInterrupt:
        pass
    except Exception as e:
        print('Error occurs at', datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
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
