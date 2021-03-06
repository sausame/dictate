#!/usr/bin/env python
# -*- coding:utf-8 -*-

import hashlib
import json
import urllib.parse

from network import Network

class Tts:

    def __init__(self, pathname):

        with open(pathname) as fp:
            self.config = json.loads(fp.read())

            self.maxLength = int(self.config['max-length'])

    def setLanguage(self, language):

        for lang in self.config['languages']:
            if language.lower() == lang['name']:
                self.language = lang
                break
        else:
            print('Not support language', language)

        self.voiceIndex = None

    def switchVoice(self):

        if self.voiceIndex is None:
            self.voiceIndex = 0
        else:
            self.voiceIndex += 1

            if self.voiceIndex >= len(self.language['voiceIds']):
                self.voiceIndex = 0

    def generateTts(self, prefix, text):

        url = self.config['url']

        accountId = self.config['accountId'] 
        secretId = self.config['secretId'] 

        preparation = self.config['preparation']
        download = self.config['download']

        languageId = self.language['languageId']
        voiceId = self.language['voiceIds'][self.voiceIndex]

        m = hashlib.md5()

        m.update(preparation['EID'].encode('utf-8'))
        m.update(languageId.encode('utf-8'))
        m.update(voiceId.encode('utf-8'))
        m.update(text.encode('utf-8'))
        m.update(preparation['IS_UTF8'].encode('utf-8'))
        m.update(preparation['EXT'].encode('utf-8'))
        m.update(accountId.encode('utf-8'))
        m.update(secretId.encode('utf-8'))

        cs = m.hexdigest()

        preparation['LID'] = languageId
        preparation['VID'] = voiceId
        preparation['ACC'] = accountId
        preparation['TXT'] = text
        preparation['CS'] = cs

        download['LID'] = languageId
        download['VID'] = voiceId
        download['ACC'] = accountId
        download['TXT'] = text
        download['CS'] = cs

        preparationUrl = '{}{}'.format(url, urllib.parse.urlencode(preparation))

        Network.get(preparationUrl)

        downloadUrl = '{}{}'.format(url, urllib.parse.urlencode(download))

        return Network.saveUrl(prefix, downloadUrl)

