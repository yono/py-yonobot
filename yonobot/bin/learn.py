#!/usr/bin/env python
# -*- coding:utf-8 -*-
from yonobot import yonobot
import datetime

if __name__ == '__main__':
    bot = yonobot.YonoBot()
    yesterday = datetime.date.today() - datetime.timedelta(days=1)
    #tweets = bot.crawl_twilog(yesterday)
    bot.learn(yesterday)
