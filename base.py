import os
import logging
import urllib.parse

import rumps
import requests
import pyperclip

class Base2FA(object):

    def __init__(self):
        self.logging = logging.getLogger(__name__)
        self.notify = Switcher()
        self.clipboard = Switcher()

    def notify_to_bark(self, title, msg, value):
        self.logging.debug(self.notify.status)
        if self.notify.status:
            title = urllib.parse.quote(title)
            msg = urllib.parse.quote(msg)
            value = urllib.parse.quote(value)
            # TODO
            for bark_url in []:
                url = f'{bark_url}/{title}/{msg}?copy={value}'
                requests.get(url)

    def notification(self, title, msg):
        self.logging.debug(self.notify.status)
        if self.notify.status:
            # cmd = '''/usr/bin/osascript -e 'display notification \"{msg}\" with title \"{title}\"' '''.format(title = title, msg = msg)
            # print(cmd)
            # os.system(cmd)
            # 切换到app通知
            rumps.notification(title = title, subtitle = msg, message = '')

    def save_to_clipboard(self, code):
        self.logging.debug(self.clipboard.status)
        if self.clipboard.status:
            pyperclip.copy(str(code))

class Switcher(object):
    
    def __init__(self):
        self._status = 1
    
    @property
    def status(self):
        return self._status
    
    @status.setter
    def status(self, status):
        self._status = status