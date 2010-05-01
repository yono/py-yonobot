#!/usr/bin/env python
# -*- coding:utf-8 -*-
import datetime
from ConfigParser import SafeConfigParser
from HTMLParser import HTMLParser
import os
import urllib2
import twoauth
from markovchains import markovchains
import twilogparser

def parse_tweet(text):
    reply = re.compile(u'@.*?')
    return reply.sub(' ', text)

class YonoBot(object):
    def __init__(self):
        self.BASE_DIR = os.path.dirname(os.path.abspath(__file__))
        self.inifile = os.path.join(self.BASE_DIR, 'settings.ini')
        self.t_ini = self._load_ini('twitter')
        self.m_ini = self._load_ini('markov')
        self.base_url = "http://twilog.org/%s/date-" % (self.t_ini['user'])
        self.m = markovchains.MarkovChains(self.m_ini['db'], 
                                           int(self.m_ini['num']))
        self.api = twoauth.api(
                           self.t_ini['consumer_key'], 
                           self.t_ini['consumer_secret'],
                           self.t_ini['access_token'], 
                           self.t_ini['access_token_secret']
                        )
        self.parser = twilogparser.TwilogParser()

    def _load_ini(self,category):
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
    
    def format_date(self,date):
        return date if len(date) == 2 else "0%s" % (date)

    def get_date_url(self, aday):
        year = str(aday.year)[2:4]
        month = self.format_date(str(aday.month))
        day = self.format_date(str(aday.day))
        return "%s%s%s" % (year,month,day)

    def crawl_twilog(self, aday):
        url = "%s%s" % (self.base_url,self.get_date_url(aday))

        fp = urllib2.urlopen(url)
        body = unicode(fp.read())

        self.parser.feed(unicode(body))
        return self.parser.sentences

    def learn(self, tweets):
        for tweet in tweets:
            sentences = tweet.split(u'。')
            for sentence in sentences:
                self.m.analyze_sentence(sentence+u'。', self.t_ini['user'])

    def post(self):
        self.api.status_update(self.m.make_sentence(user=self.t_ini['user']))
    
    def reply_to_mentions(self):
        since_id = self.get_since_id()
        mentions = self.api.mentions(since_id=since_id)

        if len(mentions) > 0:
            for status in mentions:
                screen_name = status['user']['screen_name']
                text = self.m.make_sentence(user=self.t_ini['user'])
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

if __name__ == "__main__":
    bot = YonoBot()
    yesterday = datetime.date.today() - datetime.timedelta(days=1)
    results = bot.crawl_twilog(yesterday)
    print '\n'.join(results)
