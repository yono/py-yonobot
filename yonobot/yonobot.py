#!/usr/bin/env python
# -*- coding:utf-8 -*-
import datetime
from ConfigParser import SafeConfigParser
import os
import re
import urllib2
import twoauth
from markovchains import markovchains
from twilog import twilog
import do_shiritori

def parse_tweet(text):
    reply = re.compile(u'@[\S]+')
    url = re.compile(r's?https?://[-_.!~*\'()a-zA-Z0-9;/?:@&=+$,%#]+', re.I)

    text = reply.sub('', text)
    text = url.sub('', text)
    text = text.replace(u'．', u'。')
    text = text.replace(u'，', u'、')
    text = text.replace(u'「', '')
    text = text.replace(u'」', '')
    text = text.replace(u'？', u'?')
    text = text.replace(u'！', u'!')
    return text


class YonoBot(object):

    def __init__(self):
        self.BASE_DIR = os.path.dirname(os.path.abspath(__file__))
        self.inifile = os.path.join(self.BASE_DIR, 'settings.ini')
        self.t_ini = self._load_ini('twitter')
        self.m_ini = self._load_ini('markov')
        self.m = markovchains.MarkovChains(int(self.m_ini['num']))
        self.m.load_db('mysql', self.m_ini['db'])
        self.api = twoauth.api(
                           self.t_ini['consumer_key'],
                           self.t_ini['consumer_secret'],
                           self.t_ini['access_token'],
                           self.t_ini['access_token_secret'])
        self.log = twilog.Twilog()
        self.reply = ""
        self.url = ""

    def _load_ini(self, category):
        parser = SafeConfigParser()
        parser.readfp(open(self.inifile))
        result = {}
        if category == 'markov':
            data = ['db', 'num']
        elif category == 'twitter':
            data = ['user', 'consumer_key', 'consumer_secret',
                    'access_token', 'access_token_secret']
        for d in data:
            result[d] = parser.get(category, d)
        return result

    def learn(self, aday):
        tweets = self.log.get_tweets(self.t_ini['user'], aday)
        for tweet in tweets:
            text = parse_tweet(tweet)
            sentences = text.split(u'。')
            for sentence in sentences:
                self.m.analyze_sentence(sentence + u'。', self.t_ini['user'])
        self.m.register_data()

    def say(self):
        return self.m.db.make_sentence(user=self.t_ini['user'])

    def post(self):
        self.api.status_update(self.say())

    def reply_to_mentions(self):
        since_id = self.get_since_id()
        mentions = self.api.mentions(since_id=since_id)

        shiritori = re.compile(u'^しりとり\s(.*)', re.I | re.U)
        reply_start = re.compile(u'(@.+?)\s', re.I | re.U)

        if len(mentions) > 0:
            for status in mentions:
                screen_name = status['user']['screen_name']
                to_text = reply_start.sub('', status['text'])

                if isinstance(to_text, str):
                    to_text = to_text.decode('utf-8')

                result = shiritori.search(to_text)

                if result is None:
                    text = self.m.db.make_sentence(user=self.t_ini['user'])
                else:
                    to_text = result.group().encode('utf-8')
                    text = do_shiritori.reply(to_text)
                text = "@%s %s" % (screen_name, text)
                self.api.status_update(text)

            last_since_id = mentions[-1]['id']
            self.save_since_id(last_since_id)

    def get_since_id(self):
        file = open(os.path.join(self.BASE_DIR, 'last_since_id.txt'))
        since_id = int(file.read())
        file.close()
        return since_id

    def save_since_id(self, last_since_id):
        file = open(os.path.join(self.BASE_DIR, 'last_since_id.txt'), 'w')
        file.write(str(last_since_id))
        file.close()

    def follow_users(self):
        followers_dict = {}
        followers = self.api.followers_ids()
        for follower in followers:
            followers_dict[follower] = 0

        friends_dict = {}
        friends = self.api.friends_ids()
        for friend in friends:
            friends_dict[friend] = 0

        new_followers = set(followers_dict).difference(set(friends_dict))

        for new_follower in new_followers:
            self.api.friends_create(user=new_follower)

if __name__ == "__main__":
    bot = YonoBot()
