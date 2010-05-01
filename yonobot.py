#!/usr/bin/env python
# -*- coding:utf-8 -*-
import os
import datetime
from ConfigParser import SafeConfigParser
import twoauth
from mechanize import Browser
from BeautifulSoup import BeautifulSoup, NavigableString, Declaration, Comment
import markovchains

def getNavigableStrings(soup):
    if isinstance(soup, NavigableString):
        if type(soup) not in (Comment, Declaration) and soup.strip():
            yield soup
    elif soup.name not in ('script','style'):
        for c in soup.contents:
            for g in getNavigableStrings(c):
                yield g

def parse_tweet(text):
    reply = re.compile(u'@.*?')
    return reply.sub(' ', text)

class YonoBot(object):
    def __init__(self):
        BASE_DIR = os.path.dirname(os.path.abspath(__file__))
        self.inifile = os.path.join(BASE_DIR, 'settings.ini')
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
        br = Browser()

        br.open(url)
        body = unicode(br.response().read(), br.encoding(), 'ignore')
        soup = BeautifulSoup(body)

        tweets = soup.findAll('p', {"class":"tl-text"})
        return [''.join(getNavigableStrings(t)) for t in tweets]

    def learn(self):
        tweets = self.crawl_twilog()
        for tweet in tweets:
            sentences = tweet.split(u'。')
            for sentence in sentences:
                m.analyze_sentence(sentence+u'。', self.t_ini['user'])

    def post(self):
        self.api.status_update(self.m.make_sentence(user=self.t_ini['user']))

if __name__ == "__main__":
    bot = YonoBot()
    #bot.post()
    print bot.get_date_url()
