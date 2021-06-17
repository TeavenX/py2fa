import re
import time
import base64
import poplib
import logging
from email.parser import Parser
from email.utils import parseaddr
from email.header import decode_header

from apscheduler.schedulers.blocking import BlockingScheduler

from py2fa import _notification, save_to_clipboard, config

def test_re(content):
    link_result = re.findall(r'(http.*?(licenses|validation|confirmemail|authorizedevice|verification|register|verify|activate).*?)\"', content)
    code_result = re.findall(r'(验证码|code).*?(\d{4,8})', content)
    if link_result:
        return link_result[0][0]
    if code_result:
        return code_result[0][1]
    return

class Email2FA(object):

    def __init__(self, username, password, pop_server):
        self.username = username
        self.password = password
        self.pop_server = pop_server
        self.logging = logging.getLogger(__name__)
        self.connect()
        self.email_num = self.get_email_count()
    
    def __del__(self):
        self.close()
    
    def connect(self):
        self.server = poplib.POP3_SSL(self.pop_server)
        self.server.user(self.username)
        self.server.pass_(self.password)
        self.logging.info(self.server.getwelcome())
    
    def close(self):
        self.server.close()

    def get_email_count(self):
        email_num = len(self.server.list()[1])
        return email_num
    
    def parse_title(self, title):
        title, charset = decode_header(title)[0]
        if charset:
            title = title.decode(charset)
        return title
    
    def parse_from_info(self, address):
        header, address = parseaddr(address)
        name, charset = decode_header(header)[0]
        if charset:
            name = name.decode(charset)
        return name, address
    
    def parse_content(self, content):
        # content_charset = content[0].get_content_charset()
        text_raw = self.decode_bs64(content[0].as_string().split('base64')[-1])
        # content_charset = content[1].get_content_charset()
        text_html = self.decode_bs64(content[1].as_string().split('base64')[-1])
        self.logging.debug(text_raw)
        return text_raw, text_html
    
    def decode_bs64(self, content):
        try:
            self.logging.debug(content)
            content = base64.b64decode(content).decode()
        except Exception as e:
            logging.error(e)
        return content

    def receive_email_info(self):
        rsp, msglines, msgsize = self.server.retr(self.get_email_count())
        msg_content = b'\r\n'.join(msglines).decode('utf-8')
        msg = Parser().parsestr(text=msg_content)
        temp = {}
        temp['title'] = self.parse_title(msg['Subject'])
        temp['sender'], temp['service'] = self.parse_from_info(msg['From'])
        temp['text'], temp['raw'] = self.parse_content(msg.get_payload())
        self.logging.debug(temp)
        return temp
    
    def get_code(self):
        data = self.receive_email_info()
        link_result = re.findall(r'(http.*?(licenses|validation|confirmemail|authorizedevice|verification|register|verify|activate).*?)\"', data['raw'])
        code_result = re.findall(r'(验证码|code).*?(\d{4,8})', data['text'])
        self.logging.info(link_result)
        self.logging.info(code_result)
        if link_result:
            data['code'] = link_result[0][0]
        if code_result:
            data['code'] = code_result[0][1]
        return data
    
    def notify(self):
        temp = self.get_code()
        if temp:
            self.logging.debug(temp)
            if temp.get('code'):
                _notification(temp['code'], temp['sender'] + ' - ' + temp['title'])
                save_to_clipboard(temp['code'])
    
    def update_hook(self):
        self.logging.debug('checking')
        if self.email_num < self.get_email_count():
            self.email_num = self.get_email_count()
            self.notify()

if __name__ == '__main__':
    logging.basicConfig(level = logging.INFO,format = '%(asctime)s - %(processName)s - %(lineno)d - %(name)s - %(levelname)s - %(message)s')
    logger = logging.getLogger(__name__)
    logging.getLogger("apscheduler.executors.default").setLevel(logging.ERROR)

    email_list = []
    scheduler = BlockingScheduler()
    for i in config['email']:
        email_list.append(Email2FA(i['username'], i['password'], i.get('pop_server', 'pop.' + i['username'].split('@')[1])))
    for i in email_list:
        scheduler.add_job(i.update_hook, 'interval', seconds = 3)
    
    scheduler.start()
