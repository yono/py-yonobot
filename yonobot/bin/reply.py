#!/usr/bin/env python
# -*- coding:utf-8 -*-
from yonobot import yonobot

if __name__ == '__main__':
    bot = yonobot.YonoBot()
    bot.reply_to_mentions()
