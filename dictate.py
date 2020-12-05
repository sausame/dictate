#!/usr/bin/env python
# -*- coding:utf-8 -*-

import copy
import hashlib
import json
import os
import sys
import time
import traceback
import random

from tts import Tts
from datetime import datetime
from network import Network
from utils import prRed, prGreen, prYellow, prLightPurple, prPurple, prCyan, prLightGray, prBlack, countdown, getchar, getPathnames, getProperty, reprDict, runCommand, stdinReadline, OutputPath, ThreadWritableObject

def play(pathname, speed=1):

    cmd = 'mplayer -af scaletempo -speed {} {}'.format(speed, pathname)
    runCommand(cmd)

def generateTts(tts, path, content):

    md5 = hashlib.md5(content.encode('utf8')).hexdigest()

    prefix = os.path.join(path, md5)

    pathname = '{}.mp3'.format(prefix)

    if os.path.exists(pathname):
        return pathname

    pathname = tts.generateTts(prefix, content)

    return pathname

def spell(tts, path, word):

    pathnames = list()

    for ch in word:

        ch = ch.lower()

        if ch >= 'a' and ch <= 'z':
            pathname = generateTts(tts, path, ch)
            pathnames.append(pathname)

    return pathnames

def study(configFile, ttsConfigFile, contentFile):

    MAX_NUM = 3

    path = getProperty(configFile, 'output-path')

    Network.setIsEnabled(True)
    tts = Tts(ttsConfigFile)

    tts.setLanguage('english')

    with open(contentFile) as fp:
        contentConfig = json.loads(fp.read())

        if contentConfig is None:
            print('No content')
            return

    for content in contentConfig['contents-list']:

        os.system('clear')

        print('---------------------------------------------------------------')

        print('Chinese:\n\t', content['chinese'])

        tts.switchVoice()

        word = content['word']
        print('Word:\n\t', word)

        wordPathname = generateTts(tts, path, word)
        pathnames = spell(tts, path, word)

        for index in range(MAX_NUM):

            play(wordPathname)
            time.sleep(1)

            for pathname in pathnames:
                play(pathname)
                time.sleep(0.2)

        value = stdinReadline(2)
        if 0 != len(value):
            continue

        explanation = content['explanation']
        print('Explanation:\n\t', explanation)

        tts.switchVoice()
        pathname = generateTts(tts, path, explanation)

        for index in range(MAX_NUM):
            play(pathname, 0.8)
            time.sleep(2)

        value = stdinReadline(2)
        if 0 != len(value):
            continue

        tts.switchVoice()

        samples = content['samples']

        for sample in samples:
            print('Sample:\n\t', sample)

            pathname = generateTts(tts, path, sample)

            for index in range(MAX_NUM):
                play(pathname, 0.8)

                time.sleep(2)

def test(configFile, ttsConfigFile, contentFile):

    path = getProperty(configFile, 'output-path')

    Network.setIsEnabled(True)

    tts = Tts(ttsConfigFile)
    tts.setLanguage('english')

    with open(contentFile) as fp:
        contentConfig = json.loads(fp.read())

        if contentConfig is None:
            print('No content')
            return

    random.seed()

    while len(contentConfig['contents-list']) > 0:

        contents = copy.deepcopy(contentConfig['contents-list'])

        for num in range(len(contents), 0, -1):

            num -= 1
            index = random.randint(0, num)

            content = contents.pop(index)

            tts.switchVoice()

            explanation = content['explanation']

            pathname = generateTts(tts, path, explanation)

            os.system('clear')

            print('---------------------------------------------------------------')
            print(len(contentConfig['contents-list']), 'words are left.')

            play(pathname, 0.8)

            value = stdinReadline(5, isStrip=False)
            print('Explanation:')
            print('\t', explanation)

            if 0 == len(value):
                play(pathname, 0.8)
                stdinReadline(10)

            print('Chinese:\n\t', content['chinese'])
            stdinReadline(5)

            tts.switchVoice()

            word = content['word']

            print('Word:\n\t', word)

            wordPathname = generateTts(tts, path, word)
            pathnames = spell(tts, path, word)

            play(wordPathname, 0.8)
            time.sleep(1)

            for pathname in pathnames:
                play(pathname)
                time.sleep(0.2)

            play(wordPathname, 0.8)
            time.sleep(1)

            samples = content['samples']

            print('Sample:')
            for sample in samples:

                print('\t', sample)

                pathname = generateTts(tts, path, sample)

                play(pathname, 0.8)

                time.sleep(2)

            print('Press any key except return key to skip "', word, '".')
            value = stdinReadline(10)

            if 0 == len(value):
                continue

            for index in range(len(contentConfig['contents-list'])):

                aContent = contentConfig['contents-list'][index]

                if aContent['word'] == content['word']:
                    aContent = contentConfig['contents-list'].pop(index)
                    print('"', aContent['word'], '" is skipped.')
                    break


    os.system('clear')

    message = 'You passed all the tests! Congradulations!'
    prPurple(message)

    pathname = generateTts(tts, path, message)
    play(pathname, 0.8)

def run(name, configFile):

    OutputPath.init(configFile)

    ttsConfigFile = 'templates/tts.json'

    try:
        print('Now: ', datetime.now().strftime('%Y-%m-%d %H:%M:%S'))

        sourcePath = getProperty(configFile, 'source-path')
        pathnames = getPathnames(sourcePath, '.json')

        num = len(pathnames)
        sequenceNum = -1
        
        while sequenceNum < 0 or sequenceNum >= num: 

            prGreen('Please select a lesson you want to study:');

            for index in range(num):
                pathname = pathnames[index]
                prLightPurple('{:3}\t{}'.format(index+1, pathname))

            prGreen('Please input the sequence number (default is {}):'.format(num));

            sequenceNum = stdinReadline(10)

            try:
                if len(sequenceNum) > 0:
                    sequenceNum = int(sequenceNum) - 1
                else:
                    sequenceNum = num - 1
            except ValueError as e:
                sequenceNum = num - 1

        contentFile = pathnames[sequenceNum]
        prYellow('"{}" is selected.'.format(contentFile))

        prGreen('Do you like to study or do a test?:\n\t1, study\n\t2, test\nPlease input sequence number (default is 1):')

        sequenceNum = stdinReadline(10)

        if '2' == sequenceNum:
            test(configFile, ttsConfigFile, contentFile)
        else:
            study(configFile, ttsConfigFile, contentFile)

    except KeyboardInterrupt:
        pass
    except Exception as e:
        print('Error occurs at', datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
        traceback.print_exc(file=sys.stdout)
    finally:
        pass

if __name__ == '__main__':

    if len(sys.argv) < 1:
        print('Usage:\n\t', sys.argv[0], '[config-file]\n')
        exit()

    os.environ['TZ'] = 'Asia/Shanghai'
    time.tzset()

    name = os.path.basename(sys.argv[0])[:-3] # Remove ".py"

    if len(sys.argv) > 1:
        configFile = os.path.realpath(sys.argv[1])
    else:
        configFile = 'config.ini'

    run(name, configFile)

