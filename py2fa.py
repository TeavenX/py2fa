import os
import yaml

import pyperclip

with open('config.yaml', 'r') as fp:
    config = yaml.safe_load(fp)

def _notification(title, msg):
    cmd = '''/usr/bin/osascript -e 'display notification \"{msg}\" with title \"{title}\"' '''.format(title = title, msg = msg)
    print(cmd)
    os.system(cmd)

def save_to_clipboard(code):
    pyperclip.copy(str(code))

