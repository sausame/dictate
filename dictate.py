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

from proc import Lesson
from tts import LocalTts as Tts
from datetime import datetime
from network import Network
from utils import prRed, prGreen, prYellow, prLightPurple, prPurple, prCyan, prLightGray, prBlack, countdown, getchar, getPathnames, getProperty, reprDict, runCommand, stdinReadline, OutputPath, ThreadWritableObject

def run(name, configFile):

    sourcePath = getProperty(configFile, 'source-path')
    outputPath = getProperty(configFile, 'output-path')

    lesson = Lesson(sourcePath, outputPath)
    lesson.start()

def main(argv):

    if len(argv) < 1:
        print('Usage:\n\t', argv[0], '[config-file]\n')
        exit()

    os.environ['TZ'] = 'Asia/Shanghai'
    time.tzset()

    name = os.path.basename(argv[0])[:-3] # Remove ".py"

    if len(argv) > 1:
        configFile = os.path.realpath(argv[1])
    else:
        configFile = 'config.ini'

    run(name, configFile)

if __name__ == '__main__':
    main(sys.argv)

