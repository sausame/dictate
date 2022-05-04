#!/usr/bin/env python
# -*- coding:utf-8 -*-

import copy
import hashlib
import json
import os
import random
import sys
import time
import traceback

from datetime import datetime
from network import Network
from tts import LocalTts as Tts
from utils import mkdir, runCommand
from utils import prRed, prGreen, prYellow, prLightPurple, prPurple, prCyan, prLightGray, prBlack, countdown, getchar, getPathnames, getProperty, playSound, reprDict, runCommand, stdinReadline, OutputPath, ThreadWritableObject
from word import Word

class Procedure:

    def __init__(self, dirname=None, jsonPath=None, jsonContent=None):

        if jsonPath is not None:
            with open(jsonPath) as fp:
                jsonContent = json.loads(fp.read())

        if jsonContent is None:
            return

        self.contents = jsonContent['contents-list']

        if dirname is None:
            dirname = '.'
            dirname = os.path.join(dirname, 'data')
            self.dirname = os.path.realname(dirname)
        else:
            self.dirname = dirname

        mkdir(self.dirname)

class StudyProcedure(Procedure):

    def __init__(self, dirname=None, jsonPath=None, jsonContent=None):
        super().__init__(dirname, jsonPath, jsonContent)

    def run(self):

        for content in self.contents:

            os.system('clear')
            print('---------------------------------------------------------------')

            self.studyWord(content)

    def studyWord(self, content):

        MAX_WORD_PLAYING_NUM = 3
        MAX_NUM = 1

        word = Word(self.dirname, content)

        print('Chinese:\n\t', word.chinese)
        print('Word:\n\t', word.english)

        for index in range(MAX_WORD_PLAYING_NUM):

            word.playEnglish()
            time.sleep(0.5)

            word.playChinese()
            time.sleep(0.5)

            word.playLetters()
            time.sleep(0.5)

        value = stdinReadline(2)
        if 0 != len(value):
            return

        print('Explanation:\n\t', word.explanation)
        for index in range(MAX_NUM):
            word.playExplanation()

        value = stdinReadline(2)
        if 0 != len(value):
            return

        print('Sample:\n\t', word.getSample())
        for index in range(MAX_NUM):
            word.playSample()
       

class TestProcedure(Procedure):

    def __init__(self, dirname=None, jsonPath=None, jsonContent=None):
        super().__init__(dirname, jsonPath, jsonContent)
 
    def run(self):

        random.seed()

        wholeContents = copy.deepcopy(self.contents)

        while len(wholeContents) > 0:

            contents = copy.deepcopy(wholeContents)

            for num in range(len(contents), 0, -1):

                num -= 1
                index = random.randint(0, num)

                os.system('clear')

                print('---------------------------------------------------------------')
                print(len(wholeContents), 'words are left.')

                content = contents.pop(index)
                if not self.testWord(content):
                    continue

                for index in range(len(wholeContents)):

                    aContent = wholeContents[index]

                    if aContent['word'] == content['word']:
                        aContent = wholeContents.pop(index)
                        print('"', aContent['word'], '" is skipped.')
                        break

        self.playGreeting()

    def testWord(self, content):

        word = Word(self.dirname, content)

        print('Explanation:')
        word.playExplanation()

        value = stdinReadline(5, isStrip=False)

        print('\t', word.explanation)

        if 0 == len(value):
            word.playExplanation()
            stdinReadline(5)

        print('Chinese:')
        stdinReadline(5)

        print('\t', word.chinese)
        word.playChinese()

        print('Word:')
        stdinReadline(5)

        print('\t', word.english)
        word.playEnglish()
        time.sleep(0.5)

        word.playLetters()
        time.sleep(0.5)

        print('Sample:')
        print('\t', word.getSample())

        word.playSample()

        print('Press any key except return key to skip "', word.english, '".')
        value = stdinReadline(10)

        return (len(value) > 0)

    def playGreeting(self):

        os.system('clear')

        message = 'You passed all the tests! Congradulations!'
        prPurple(message)

        pathname = generateTts(tts, path, message, 0.8)
        playSound(pathname)


class Lesson:

    def __init__(self, lessonDir, dirname=None):

        self.lessonDir = lessonDir
        self.dirname = dirname

    def start(self):

        try:
            print('Now: ', datetime.now().strftime('%Y-%m-%d %H:%M:%S'))

            pathnames = getPathnames(self.lessonDir, '.json')
            pathnames = sorted(pathnames, reverse=True)

            num = len(pathnames)
            sequenceNum = -1
            
            while sequenceNum < 0 or sequenceNum >= num: 

                prGreen('Please select a lesson you want to study:');

                for index in range(num):
                    pathname = pathnames[index]
                    prLightPurple('{:3}\t{}'.format(index+1, pathname))

                prGreen('Please input the sequence number (default is {}):'.format(num));

                sequenceNum = stdinReadline(20, isPrompt=False)

                try:
                    if len(sequenceNum) > 0:
                        sequenceNum = int(sequenceNum) - 1
                    else:
                        sequenceNum = num - 1
                except ValueError as e:
                    sequenceNum = num - 1

            contentFile = pathnames[sequenceNum]
            prYellow('"{}" is selected.'.format(contentFile))

            prGreen('Do you like to study or do a test?:\n\t1, study\n\t2, test\nPlease input sequence number (default is 2):')

            sequenceNum = stdinReadline(20, isPrompt=False)

            if '1' == sequenceNum:
                procedure = StudyProcedure(self.dirname, contentFile)
            else:
                procedure = TestProcedure(self.dirname, contentFile)

            procedure.run()

        except KeyboardInterrupt:
            pass
        except Exception as e:
            print('Error occurs at', datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
            traceback.print_exc(file=sys.stdout)
        finally:
            pass



