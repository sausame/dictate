#!/usr/bin/env python
# -*- coding:utf-8 -*-

import os
import random
import sys
import time
import traceback

from datetime import datetime
from tts import LocalTts as Tts
from utils import getchar, prGreen, prYellow, prLightPurple, prPurple, prCyan, prLightGray, prBlack, stdinReadline

class Character:

    def __init__(self, doubleProportion=0.0, tripleProportion=0.0, separateNumber=3):
        self.doubleProportion = doubleProportion
        self.tripleProportion = tripleProportion

        self.separateNumber = separateNumber

    def createOne(self):
        pass

    def create(self, length):

        self.str = ''
        self.chars = ''

        count = 0

        while length > 0:

            dup = self.getDupNumber(length, count)
            char, src = self.createOne()

            for i in range(dup):
                self.chars += '{}'.format(char)

            length -= dup
            count += dup

            if 2 == dup:
                self.str += ' double'
            elif 3 == dup:
                self.str += ' triple'

            self.str += ' {}'.format(src)

            if 0 == count % self.separateNumber:
                self.str += ','

        self.str += '.'

    def getDupType(self):

        ratio = random.random()

        if ratio < self.doubleProportion:
            return 2

        if ratio < self.doubleProportion + self.tripleProportion:
            return 3

        return 1

    def getDupNumber(self, maxlen, count):

        num = self.getDupType()
        if maxlen < num:
            num = maxlen

        remainedNum = self.separateNumber - count % self.separateNumber
        if (num > remainedNum):
            num = remainedNum

        return num

    def check(self):
        pass

class NumberCharacter(Character):

    def __init__(self, doubleProportion=0.2, tripleProportion=0.2):
        super().__init__(doubleProportion, tripleProportion, 4)

    def createOne(self):
        num = random.randint(0, 9)

        if 0 == num:
            src = 'o'
        else:
            src = '{}'.format(num)

        return num, src

class PostCodeCharacter(Character):

    def __init__(self, doubleProportion=0.2, tripleProportion=0.2):
        super().__init__(doubleProportion, tripleProportion, 3)

    def createOne(self):
        num = random.randint(0, 35)

        if 0 == num:
            src = 'zero'
        elif num < 10:
            src = '{}'.format(num)
        else:
            ''' chr(65) == A '''
            num = chr(num + 55)

            if num in ['C', 'H', 'W']:
                src = ',' + num
            else:
                src = num

        return num, src

class CharacterFactory:

    NUMBER_CHARACTER_TYPE = 0
    POST_CODE_CHARACTER_TYPE = 1

    def create(charType = 0):

        if CharacterFactory.NUMBER_CHARACTER_TYPE == charType:
            return NumberCharacter()

        if CharacterFactory.POST_CODE_CHARACTER_TYPE == charType:
            return PostCodeCharacter()

        return None

class Examiner:

    MAX_RETRIED_NUM = 5

    def __init__(self):
        random.seed()

        self.tts = Tts()
        self.tts.setLanguage('english')

    def testOne(self, character):

        chars = character.chars.upper()

        for index in range(Examiner.MAX_RETRIED_NUM):
            self.tts.say(character.str)

            guess = input()
            guess = guess.strip().replace(' ', '').replace(',', '').upper()

            if guess == chars:
                break

            os.system('clear')

            print('Please try it again')
            stdinReadline(2)
            print('')

        else:
            print('It is', chars)
            self.tts.say(character.str)

        return index

    def testLoop(self, length, size, charType = 0):

        count = 0
        times = 0

        char = CharacterFactory.create(charType)

        for index in range(size):

            os.system('clear')

            print('NO.', index + 1, ': please be ready ...')
            stdinReadline(1)
            print('')

            char.create(length)

            repeatedTimes = self.testOne(char)
            if 0 == repeatedTimes:
                count += 1

            times += repeatedTimes

        print('All retried times:', times)
        print('Accurate:', count)

    def test(self):
        prGreen('Please input the length (default is 6):')

        length, _ = stdinReadline(2)
        if '' == length:
            length = 6
        else:
            length = int(length)

        prCyan('The length is {}'.format(length))

        prGreen('Please input the number (default is 10):')

        size, _ = stdinReadline(2)
        if '' == size:
            size = 10
        else:
            size = int(size)

        prCyan('The size is {}'.format(size))

        prGreen('Please input the type [0: number, 1: post code] (default is 0):')

        charType, _ = stdinReadline(5)
        if '' == charType:
            charType = 0
        else:
            charType = int(charType)

        prCyan('The type is {}'.format(charType))

        self.testLoop(length, size, charType)

def main(argv):

    os.environ['TZ'] = 'Asia/Shanghai'
    time.tzset()

    try:
        print('Now: ', datetime.now().strftime('%Y-%m-%d %H:%M:%S'))

        examiner = Examiner()
        examiner.test()
    except KeyboardInterrupt:
        pass
    except Exception as e:
        print('Error occurs at', datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
        traceback.print_exc(file=sys.stdout)
    finally:
        pass

if __name__ == '__main__':
    main(sys.argv)
