import os
import re
import time
import logging
import sqlite3

from base import Base2FA

class LiteDB(object):
    def __init__(self, db_file):
        self.db_file = db_file
    
    def dict_factory(self, cursor, row): 
        dict_c = {} 
        for idx, col in enumerate(cursor.description): 
            dict_c[col[0]] = row[idx] 
        return dict_c

    def conn(self):
        conn = sqlite3.connect(self.db_file)
        conn.row_factory = self.dict_factory
        cursor = conn.cursor()
        return conn, cursor
    
    def select(self, sql):
        conn, cursor = self.conn()
        result = list(cursor.execute(sql))
        conn.commit()
        conn.close()
        return result


class Message2FA(Base2FA):
    def __init__(self, db_file):
        super(Message2FA, self).__init__()
        self.db_file = db_file
        self.db = LiteDB(self.db_file)
        self.update_time = int(time.time())
    
    def get_message(self):
        sql = """
        select
            message.rowid,
            ifnull(handle.uncanonicalized_id, chat.chat_identifier) AS sender,
            message.service,
            (message.date / 1000000000 + 978307200) AS message_date,
            message.text
        from
            message
                left join chat_message_join
                        on chat_message_join.message_id = message.ROWID
                left join chat
                        on chat.ROWID = chat_message_join.chat_id
                left join handle
                        on message.handle_id = handle.ROWID
        where
            is_from_me = 0
            and text is not null
            and length(text) > 0
            and (
                text glob '*[0-9][0-9][0-9][0-9]*'
                or text glob '*[0-9][0-9][0-9][0-9][0-9]*'
                or text glob '*[0-9][0-9][0-9][0-9][0-9][0-9]*'
                or text glob '*[0-9][0-9][0-9][0-9][0-9][0-9][0-9]*'
                or text glob '*[0-9][0-9][0-9][0-9][0-9][0-9][0-9][0-9]*'
            )
        order by
            message.date desc
        limit 10
        """
        data = self.db.select(sql)
        return data
    
    def get_code(self):
        self.logging.debug('select db')
        msgs = self.get_message()
        result = []
        for i in msgs:
            if 'code' in i['text'] or '码' in i['text']:
                i['code'] = re.findall(r'([0-9]{4,8})', i['text'])
                if i['code']:
                    i['code'] = i['code'][0]
                    result.append(i)
        return result
    
    def _notify(self):
        temp = self.get_code()[0]
        self.logging.debug(temp)
        if int(time.time()) - int(temp['message_date']) < 30:
            self.notification(temp['code'], temp['text'])
            self.notify_to_bark(temp['code'], temp['text'], temp['code'])
            self.save_to_clipboard(temp['code'])
    
    def update_hook(self):
        self.logging.debug('checking')
        update_time = int(os.path.getmtime(self.db_file))
        tp = abs(update_time - self.update_time)
        if not tp and tp <= 15:
            self.update_time = update_time
            self._notify()