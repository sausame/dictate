#!/usr/bin/env python
# -*- coding:utf-8 -*-

# Utils
import binascii
import hashlib
import json
import os
import platform
import random
import re
import select
import stat
import sys
import subprocess
import threading
import time

from datetime import tzinfo, timedelta, datetime
from pytimedinput import timedKey

def seconds2Datetime(seconds):
    #return time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(seconds))
    return datetime.fromtimestamp(seconds).strftime('%Y-%m-%d %H:%M:%S')

def datetime2Seconds(dt):
    return time.mktime(datetime.strptime(dt, '%Y-%m-%d %H:%M:%S').timetuple())
    # return (datetime.strptime(dt, '%Y-%m-%d %H:%M:%S') - datetime(1970, 1, 1)).total_seconds() # XXX CTS

def duration2srttime(duration):
    # [hours]:[minutes]:[seconds],[milliseconds]

    hours = int(duration/3600) 
    duration -= hours * 3600

    minutes = int(duration/60) 
    duration -= minutes * 60

    seconds = int(duration)
    duration -= seconds

    milliseconds = int(duration * 1000)

    return '{:02d}:{:02d}:{:02d},{:03d}'.format(hours, minutes,
            seconds, milliseconds)

def randomSleep(minS, maxS):
    time.sleep(random.uniform(minS, maxS))

def countdown(t): 
    
    while t: 
        mins, secs = divmod(t, 60) 
        timer = '{:02d}:{:02d}'.format(mins, secs) 
        print(timer, end="\r") 
        time.sleep(1) 
        t -= 1

def stdinReadline(timeout=0, isStrip=True, isPrompt=True):

    content = ''
    isTimeout = False

    for index in range(1):

        if timeout <= 0:
            content = sys.stdin.readline()
            break

        isTimeout = True

        while timeout: 

            if isPrompt:
                mins, secs = divmod(timeout, 60) 
                timer = '{:02d}:{:02d}'.format(mins, secs) 
                print('\033[91m{}\033[00m'.format(timer), end='\r') 

            inputFlag, _, _ = select.select([sys.stdin], [], [], 1)

            if inputFlag:
                isTimeout = False
                content = sys.stdin.readline()
                break

            timeout -= 1

    if isStrip:
        content = content.strip()

    return content, isTimeout

def mkdir(path, mode=stat.S_IRUSR|stat.S_IWUSR|stat.S_IXUSR|stat.S_IRGRP|stat.S_IWGRP|stat.S_IXGRP|stat.S_IROTH|stat.S_IWOTH|stat.S_IXOTH):
    if not os.path.exists(path):
        os.mkdir(path, mode)

    chmod(path, mode)

def chmod(path, mode=stat.S_IRUSR|stat.S_IWUSR|stat.S_IXUSR|stat.S_IRGRP|stat.S_IWGRP|stat.S_IXGRP|stat.S_IROTH|stat.S_IWOTH|stat.S_IXOTH):
    if os.path.exists(path):
        try:
            os.chmod(path, mode)
        except PermissionError as e:
            print(e)

def remove(path):
    if os.path.exists(path):
        os.remove(path)

def getPathnames(dirpath, suffix=None):

    pathnames = list()

    for root, dirs, files in os.walk(dirpath, topdown=False):
        for name in files:
            if suffix is not None and not name.endswith(suffix):
                continue

            pathname = os.path.join(root, name)
            pathnames.append(pathname)

    pathnames = sorted(pathnames)

    return pathnames

def getMd5(content):

    md5_hash = hashlib.md5()  
    md5_hash.update(content.encode('utf-8'))  

    return md5_hash.hexdigest()  

def getFileMd5(path):

    if not os.path.exists(path):
        return None

    with open(path) as fp:
        content = fp.read()
        return getMd5(content)

    return None

def getch(timeout=-1, isPrompt=True):

    if isPrompt:
        print('Please press return key to continue')

    INTERVAL = 1

    if timeout > 0: 
        while timeout > 0: 

            if isPrompt:
                mins, secs = divmod(timeout, 60) 
                timer = '{:02d}:{:02d}'.format(mins, secs) 
                print('\033[91m{}\033[00m'.format(timer), end='\r') 

            inputFlag, _, _ = select.select([sys.stdin], [], [], INTERVAL)
            if inputFlag:
                return sys.stdin.read(1), False

            timeout -= INTERVAL
        else:
            return None, True

    return sys.stdin.read(1), True

def getchar(timeout=-1, promptPrefix='Press any key to continue', isPrompt=True):

    if isPrompt:
        if timeout > 0:
            prompt = '{} in {} seconds.\n'.format(promptPrefix, timeout)
        else:
            prompt = '{}.\n'.format(promptPrefix, timeout)
    else:
        prompt = ''

    return timedKey(prompt=prompt, timeout=timeout)

def atoi(src):
    if isinstance(src, int):
        return src
    if isinstance(src, str) or isinstance(src, unicode):
        n = 0
        for c in src.lstrip():
            if c.isdigit():
                n *= 10
                n += int(c)
            else:
                break
        return n
    return 0

def slugify(value):
    return "".join(x for x in value if x.isalnum())

def toVisibleAscll(src):

    if None == src or 0 == len(src):
        return src

    if unicode != type(src):
        try:
            src = unicode(src, errors='ignore')
        except TypeError as e:
            print('Unable to translate {!r} of type {}'.format(src, type(src)), ':', e)

    dest = ''

    for char in src:
        if char < chr(32): continue
        dest += char

    return dest

def hexlifyUtf8(src):
    return binascii.hexlify(src.encode('utf-8', 'ignore'))

def unhexlifyUtf8(src):
    return binascii.unhexlify(src).decode('utf-8', 'ignore')

def runCommand(cmd, shell=False):

    process = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

    output, unused_err = process.communicate()
    retcode = process.poll()

    if retcode != 0:
        raise subprocess.CalledProcessError(retcode, cmd)

    return output

def displayImage(path):

    os = platform.system()

    if os == 'Darwin':
        subprocess.call(['open', path])
    elif os == 'Linux':
        subprocess.call(['xdg-open', path])
    else:
        os.startfile(path)

def playSound(pathname, speed=1):
    cmd = 'mplayer -af scaletempo -speed {} {}'.format(speed, pathname)
    runCommand(cmd)

# The notifier function
def notify(title, subtitle, message):

    system = platform.system()

    if system == 'Darwin':
        t = '-title {!r}'.format(title)
        s = '-subtitle {!r}'.format(subtitle)
        m = '-message {!r}'.format(message)
        os.system('terminal-notifier {}'.format(' '.join([m, t, s])))
    elif system == 'Linux':
        pass
    else:
        pass

# update property of name to value
def updateProperty(path, name, value):
    fp = None
    targetLine = None
    newLine = None
    try:
        fp = open(path)
        minlen = len(name) + 1
        for line in fp:
            if len(line) < minlen or '#' == line[0]:
                continue
            group = line.strip().split('=')
            if 2 != len(group) or group[0].strip() != name:
                continue
            if group[1] == value:
                return None
            else:
                targetLine = line
                newLine = '{}={}\r\n'.format(name,value)
                break
    except IOError:
        pass
    finally:
        if fp != None: fp.close()

    if targetLine != None and newLine != None:
        with open(path) as fp:
            content = fp.read()

        content = content.replace(targetLine, newLine)

        with open(path, 'w') as fp:
            fp.write(content)

    return None

def getProperty(path, name):

    fp = None

    try:
        fp = open(path)

        minlen = len(name) + 1

        for line in fp:
            if len(line) < minlen or '#' == line[0]:
                continue

            line = line.strip()
            pos = line.find('=')

            if pos < 0:
                continue

            if line[:pos] != name:
                continue

            return line[pos+1:].strip()

    except IOError:
        pass

    finally:
        if fp != None: fp.close()

    return None

def safePop(obj, name, defaultValue=None):

    try:
        return obj.pop(name)
    except KeyError:
        pass

    return defaultValue

def getMatchString(content, pattern):

    matches = re.findall(pattern, content)

    if matches is None or 0 == len(matches):
        return None

    return matches[0]

def dump(obj):

    def dumpObj(obj):

        fields = ['    {}={}'.format(k, v)
            for k, v in obj.__dict__.items() if not k.startswith('_')]

        return ' {}:\n{}'.format(obj.__class__.__name__, '\n'.join(fields))

    if obj is None: return None

    if type(obj) is list:

        for subObj in obj:
            dump(subObj)
    else:
        print(dumpObj(obj))

def reprDict(data, indent=4):
    return json.dumps(data, ensure_ascii=False, indent=indent, sort_keys=True)

# XXX: Gentlemen should not force ladies to quit but ask them to quit.
class LadyThread(threading.Thread):

    def __init__(self):

        self.isInitialized = False

        self.running = True
        threading.Thread.__init__(self)

        self.mutex = threading.Lock()

    def run(self):

        threadname = threading.currentThread().getName()

        while self.running:

            self.mutex.acquire()

            self.runOnce()

            self.mutex.release()

        print('Quit')

    def runOnce(self):
        raise TypeError('No implement')

    def sleep(self, seconds):

        while self.running and seconds > 0:
            seconds -= 1
            time.sleep(1)

    def quit(self):

        print('Stopping ...')
        self.running = False

class AutoReleaseThread(threading.Thread):

    def __init__(self):

        self.isInitialized = False

        self.running = True
        threading.Thread.__init__(self)

        self.mutex = threading.Lock()

    def initialize(self):

        try:
            self.mutex.acquire()

            if not self.isInitialized:

                self.isInitialized = True

                self.onInitialized()

            self.accessTime = time.time()

        except KeyboardInterrupt:
            raise KeyboardInterrupt

        finally:
            self.mutex.release()

    def release(self):

        self.isInitialized = False

        self.onReleased()

    def run(self):

        threadname = threading.currentThread().getName()

        while self.running:

            self.mutex.acquire()

            if self.isInitialized:

                diff = time.time() - self.accessTime

                if diff > 30: # 30 seconds
                    self.release()

            self.mutex.release()

            time.sleep(1)

        else:
            self.release()

        print('Quit')

    def quit(self):

        print('Stopping ...')
        self.running = False

class OutputPath:

    LOG_OUTPUT_PATH = None
    DATA_OUTPUT_PATH = None

    @staticmethod
    def init(configFile):

        outputPath = getProperty(configFile, 'output-path')
        outputPath = os.path.realpath(outputPath)

        mkdir(outputPath)

        OutputPath.LOG_OUTPUT_PATH = os.path.join(outputPath, 'logs')
        mkdir(OutputPath.LOG_OUTPUT_PATH)

        path = os.path.join(outputPath, 'datas')
        mkdir(path)

        OutputPath.DATA_OUTPUT_PATH = os.path.join(path, datetime.now().strftime('%Y_%m_%d'))
        mkdir(OutputPath.DATA_OUTPUT_PATH)

    @staticmethod
    def createDataPath(name):

        path = OutputPath.getDataPath(name)
        mkdir(path)

    @staticmethod
    def getDataPath(name):

        name = slugify(name)
        return os.path.join(OutputPath.DATA_OUTPUT_PATH, name)

class ThreadWritableObject(threading.Thread):

    def __init__(self, configFile, name, log=None):

        threading.Thread.__init__(self)

        self.running = True

        if log is not None:
            self.path = os.path.realpath(log)
        else:
            self.path = os.path.join(OutputPath.LOG_OUTPUT_PATH, '{}.log'.format(name))

        self.contents = []

        self.mutex = threading.Lock()

    def write(self, content):

        self.mutex.acquire()

        self.contents.append(content)

        self.mutex.release()

    def flush(self):
        pass

    def run(self):

        def output(path, contents):

            with open(path, 'a') as fp:

                for content in contents:
                    fp.write(content)

        threadname = threading.currentThread().getName()

        continueEmptyCount = 0

        while self.running:

            self.mutex.acquire()

            if 0 != len(self.contents):

                continueEmptyCount = 0

                MAX_SIZE = 2*1024*1024

                if os.path.exists(self.path) and os.stat(self.path).st_size > MAX_SIZE:

                    os.rename(self.path, '{}.old'.format(self.path))

                output(self.path, self.contents)

                del self.contents[:]

            else:

                continueEmptyCount += 1

                if 0 == continueEmptyCount % 6: # 1 minute
                    content = 'No output at {}\n'.format(datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
                    output(self.path, [content])

            self.mutex.release()

            time.sleep(10)

        else:
            output(self.path, self.contents)

    def quit(self):

        print('Quit ...')
        self.running = False

def removeOverdueFiles(pathname, seconds, suffix=None):

    now = time.time()

    for parent, dirnames, filenames in os.walk(pathname):

        for filename in filenames:

            path = os.path.join(parent, filename)

            if None != suffix and not filename.endswith(suffix):
                continue

            if now > os.path.getctime(path) + seconds:
                # Remove
                os.remove(path)

# Python program to print 
# colored text and background 
class colors: 
    ''' Colors class:reset all colors with colors.reset; two  
    sub classes fg for foreground  
    and bg for background; use as colors.subclass.colorname. 
    i.e. colors.fg.red or colors.bg.greenalso, the generic bold, disable,  
    underline, reverse, strike through, 
    and invisible work with the main class i.e. colors.bold
    '''

    reset='\033[0m'
    bold='\033[01m'
    disable='\033[02m'
    underline='\033[04m'
    reverse='\033[07m'
    strikethrough='\033[09m'
    invisible='\033[08m'

    class fg: 
        black='\033[30m'
        red='\033[31m'
        green='\033[32m'
        orange='\033[33m'
        blue='\033[34m'
        purple='\033[35m'
        cyan='\033[36m'
        lightgrey='\033[37m'
        darkgrey='\033[90m'
        lightred='\033[91m'
        lightgreen='\033[92m'
        yellow='\033[93m'
        lightblue='\033[94m'
        pink='\033[95m'
        lightcyan='\033[96m'

    class bg: 
        black='\033[40m'
        red='\033[41m'
        green='\033[42m'
        orange='\033[43m'
        blue='\033[44m'
        purple='\033[45m'
        cyan='\033[46m'
        lightgrey='\033[47m'

# Python program to print 
# colored text and background 
def prRed(skk): print("\033[91m {}\033[00m" .format(skk)) 
def prGreen(skk): print("\033[92m {}\033[00m" .format(skk)) 
def prYellow(skk): print("\033[93m {}\033[00m" .format(skk)) 
def prLightPurple(skk): print("\033[94m {}\033[00m" .format(skk)) 
def prPurple(skk): print("\033[95m {}\033[00m" .format(skk)) 
def prCyan(skk): print("\033[96m {}\033[00m" .format(skk)) 
def prLightGray(skk): print("\033[97m {}\033[00m" .format(skk)) 
def prBlack(skk): print("\033[98m {}\033[00m" .format(skk)) 


