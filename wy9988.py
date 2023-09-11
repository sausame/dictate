#!/usr/bin/env python
# -*- coding:utf-8 -*-

import os
import random
import re
import sys
import time
import traceback

from datetime import datetime
from tts import LocalTts as Tts
from utils import getch, getchar, getPathnames, getProperty, prGreen, prYellow, prLightPurple, prPurple, prCyan, prLightGray, prBlack, stdinReadline

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

        lines = []

        with open(pathname) as fp:
            lines = fp.read().splitlines()

            if len(lines) == 0:
                return

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

        print(len(lane1), len(lane2))

        for index in range(len(lane1)):
            print(lane1[index], '\t', lane2[index])

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
                lane.append(string)
                return

            string = ' '.join(newSegments[:position])
            lane.append(string)

            string = ' '.join(newSegments[position:])
            string = Explanation.get(self.phrase, string)
            lane.append(string)

        lineType = len(lane) % 2
        if 0 == lineType:
            appendText(lane, line)
            return

        string = Explanation.get(self.phrase, line)
        lane.append(string)

def run(name, configFile):

    try:
        synonymPath = getProperty(configFile, 'synonym-path')

        phrase = Phrase()

        page = SynonymPage(phrase)
        page.parse('./english/synonym/9988/unit-b1-1.txt')
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
