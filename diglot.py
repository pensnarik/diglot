#!/usr/bin/env python3

import os
import re
import json
import time
import requests
from mutex.db import db

class Wrapper(object):

    def __init__(self):
        self.commands = dict()

    def command(self, commands, **args):
        def decorator(f):
            for cmd in commands:
                self.commands[cmd] = f
        return decorator

wrapper = Wrapper()

class Message(object):


    def __init__(self, data):
        if 'message' not in data:
            return
        self.message_id = data['message']['message_id']
        self.text = data['message']['text']
        self.user_id = data['message']['from']['id']

class App(object):

    newTranslations = dict()
    replyKeyboard = {'keyboard': [['Play'], ['Add new translation'], ['I don\'t know', 'Statistics']]}

    def __init__(self):
        self.token = os.environ.get('DIGLOT_TOKEN')
        if self.token is None:
            raise Exception('Environment variable $DIGLOT_TOKEN is not defined')
        self.url = 'https://api.telegram.org/bot%(token)s/%(method)s'
        self.update_id = 1

    def getNextWord(self, user_id):
        qGetWord = '''
        select * from public.get_next_word(%(user_id)s)
        '''
        result = db.query_dict(qGetWord, {'user_id': user_id})
        if len(result) == 0:
            return None
        return {'from': result[0]['word_from'], 'job_id': result[0]['job_id']}

    def sendMessage(self, to, text, use_markdown=False):
        if isinstance(to, str):
            to = self.getUserByAlias(to).get('id')
        data = {'chat_id': to, 'text': text[:4095]}
        if use_markdown:
            data.update({'parse_mode': 'Markdown'})
        data.update({'reply_markup': json.dumps(self.replyKeyboard)})
        print(data)
        result = requests.post(self.url % {'token': self.token, 'method': 'sendMessage'}, data=data)
        if result != 200:
            print(result.text)

    def getUpdates(self):
        try:
            r = requests.get(self.url % {'token': self.token,
                                         'method': 'getUpdates'}, data={'offset': self.update_id})
            return json.loads(r.text)
        except Exception:
            print("Ecxeption!")
            return {'result': list()}

    def checkUserAnswer(self, user_id, answer):
        qCheckAnswer = '''
        select * from public.check_user_answer(%(user_id)s, %(answer)s)
        '''
        result = db.query_dict(qCheckAnswer, {'user_id': user_id, 'answer': answer})[0]
        if answer is None:
            self.sendMessage(user_id, 'Oh, I\'m so sorry \U0001f625. The correct answer was: *%s*' % result['correct_answer'], use_markdown=True)
        elif result['is_correct']:
            self.sendMessage(user_id, 'Your answer is correct')
        else:
            self.sendMessage(user_id, 'Your answer is wrong')

    @wrapper.command(['/new', 'Add new translation'])
    def command_new(self, user_id, *args):
        self.sendMessage(user_id, 'Enter word in English')
        self.newTranslations[user_id] = {'status': 'waiting_for_en'}

    @wrapper.command(['/play', 'Play'])
    def command_play(self, user_id, *args):
        word = self.getNextWord(user_id)
        if word:
            self.sendMessage(user_id, 'Give me a translation for word: *%s*' % word['from'], use_markdown=True)
        else:
            self.sendMessage(user_id, 'There are jobs for you, relax')

    @wrapper.command(['/stat', 'Statistics'])
    def command_stat(self, user_id, *args):
        result = db.query_dict('select * from get_statistics(%(user_id)s)', {'user_id': user_id})[0]
        self.sendMessage(user_id, 'Total words: %s, total jobs: %s, correct answers: %s' % \
            (result['total_words'], result['total_jobs'], result['correct_answers']))

    def addNewTranslation(self, user_id):
        qAddNewTranslation = '''
        select public.create_translation(%(user_id)s, %(from)s, %(to)s)
        '''
        for word in self.newTranslations[user_id]['ru'].split(','):
            db.query_value(qAddNewTranslation, {'from': self.newTranslations[user_id]['en'],
                                                'to': word.lower().strip(),
                                                'user_id': user_id})
        del self.newTranslations[user_id]
        return

    def getCurrentJobID(self, user_id):
        qGetCurrentJobID = '''
        select public.get_current_job(%(user_id)s)
        '''
        result = db.query_value(qGetCurrentJobID, {'user_id': user_id})
        return result

    @wrapper.command(['/giveup', 'I don\'t know'])
    def command_giveup(self, user_id, *args):
        self.checkUserAnswer(user_id, None)

    def loop(self):
        while True:
            updates = self.getUpdates()
            for update in updates.get('result', []):
                print(update)
                if 'message' not in update:
                    print('Skipping not-message update')
                    continue
                m = Message(update)

                if m.text.startswith('/') or m.text in ('Play', 'Add new translation', 'I don\'t know'):
                    if m.text.startswith('/'):
                        command = m.text.split(' ')[0]
                    else:
                        command = m.text
                    args = re.sub('^%s' % command, '', m.text)
                    if command in wrapper.commands:
                        wrapper.commands[command](self, m.user_id, args.strip())
                elif m.user_id in self.newTranslations:
                    if self.newTranslations[m.user_id]['status'] == 'waiting_for_en':
                        self.newTranslations[m.user_id]['en'] = m.text
                        self.newTranslations[m.user_id]['status'] = 'waiting_for_ru'
                        self.sendMessage(m.user_id, 'Enter word in Russian')
                    elif self.newTranslations[m.user_id]['status'] == 'waiting_for_ru':
                        self.newTranslations[m.user_id]['ru'] = m.text
                        self.addNewTranslation(m.user_id)
                        self.sendMessage(m.user_id, 'Your translation was accepted')
                elif self.getCurrentJobID(m.user_id) is not None:
                    # We suppose to user playing, let's check his answer
                    self.checkUserAnswer(m.user_id, m.text)
                else:
                    pass

                self.update_id = int(update['update_id']) + 1
            time.sleep(1)

    def run(self):
        self.loop()

if __name__ == '__main__':
    app = App()
    dsn = os.environ.get('DIGLOT_DB')
    if dsn is None:
        raise Exception('Could not connect to database: $DIGLOT_DB environment variable is not defined')
    db.connect(dsn)
    app.run()
