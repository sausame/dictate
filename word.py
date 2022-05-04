#!/usr/bin/env python
# -*- coding:utf-8 -*-

import copy
import hashlib
import os
import time

from tts import LocalTts as Tts
from utils import playSound, runCommand

class Word:

    def __init__(self, dirname, content):

        self.dirname = dirname

        self.chinese = content['chinese'].strip()
        self.english = content['word'].strip()
        self.explanation = content['explanation'].strip()
        self.samples = copy.deepcopy(content['samples'])

        self.initLetters()

    def set(self, dirname):
        self.dirname = dirname

    def initLetters(self):

        if 0 == len(self.english):
            self.letters = None
            return

        self.letters = list()

        for ch in self.english:
            ch = ch.lower()
            if ch >= 'a' and ch <= 'z':
                self.letters.append(ch)

    def getSample(self, index=0):

        if index >= len(self.samples):
            return ''

        return self.samples[index]

    def generateTts(self, content, language='english', speed=1.0):

        content = content.strip()
        if 0 == len(content):
            return None

        md5 = hashlib.md5(content.encode('utf8')).hexdigest()
        prefix = os.path.join(self.dirname, md5)

        pathname = '{}.mp3'.format(prefix)
        if os.path.exists(pathname):
            return pathname

        tts = Tts()
        tts.setLanguage(language)

        pathname = tts.generateTts(prefix, content, speed)

        return pathname

    def playChinese(self):
        pathname = self.generateTts(self.chinese, 'chinese')
        playSound(pathname)

    def playEnglish(self):
        pathname = self.generateTts(self.english)
        playSound(pathname)

    def playExplanation(self):
        pathname = self.generateTts(self.explanation)
        playSound(pathname)

    def playSample(self, index=0):

        if index >= len(self.samples):
            return

        sample = self.samples[index]

        pathname = self.generateTts(sample)
        playSound(pathname)

    def playLetters(self):

        pathnames = list()

        for letter in self.letters:
            pathname = self.generateTts(letter)
            playSound(pathname)
            time.sleep(0.1)

        return pathnames

