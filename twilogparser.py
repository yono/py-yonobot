#!/usr/bin/env python
# -*- coding:utf-8 -*-
from HTMLParser import HTMLParser

class TwilogParser(HTMLParser):

    def __init__(self):
        HTMLParser.__init__(self)
        self.flag = False
        self.words = []
        self.sentences = []
    
    def handle_starttag(self, tag, attrs):
        attrs_dic = dict(attrs)

        if tag == 'p' and 'class' in attrs_dic:
            if attrs_dic['class'] == 'tl-text':
                self.flag = True

    def handle_data(self, data):
        if self.flag:
            self.words.append(data)

    def handle_endtag(self, tag):
        if tag == 'p':
            sentence = ''.join(self.words)
            if sentence != '':
                self.sentences.append(sentence)
            self.words = []
            self.flag = False

    #def feed(self, data):
    #    HTMLParser.feed(data)
    #    return self.sentences

if __name__ == '__main__':
    file = open('/Users/yono/Desktop/test.html').read()

    parser = TwilogParser()
    parser.feed(file)
    result = parser.sentences

    print '\n'.join(result)
