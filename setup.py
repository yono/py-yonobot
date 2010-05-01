#!/usr/bin/env python
# -*- coding:utf-8 -*-

from distutils.core import setup

setup(
    name="yonobot",
    version="0.1",
    packages=['yonobot'],
    scripts=['yonobot/bin/post.py',
             'yonobot/bin/learn.py'],
)
