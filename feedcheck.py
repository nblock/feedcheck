#!/usr/bin/python2
# -*- coding: utf-8 -*-
'''
File    : feedcheck.py
Author  : Florian Preinstorfer
Contact : nblock [/at\] archlinux DOT us
Date    : 20.09.2011
License : GPLv3

Description : Check feed availability from an opml file.

Requirements: python2, requests, feedparser
'''
from xml.etree import ElementTree
import Queue
import threading
import feedparser
import requests
import time
import datetime

THREADS = 1
MAX_AGE_IN_DAYS = 365

class Feedcheck(threading.Thread):
    '''Check availability of feeds.'''

    def __init__( self, queue ):
        threading.Thread.__init__(self)
        self.queue = queue
        self.now = datetime.datetime.now()
        self.timedelta = datetime.timedelta(days=MAX_AGE_IN_DAYS)

    def run(self):
        while True:
            item = self.queue.get()
            res = requests.get(item)
            proceed = True
            #print(item)
            
            #status code other than 200
            if res.status_code != 200:
                print("status code '{}' -> '{}'".format(res.status_code, item))
                proceed = False
               
            if proceed:
                fp = feedparser.parse(res.content)

                #try to get last updated date
                if fp.feed.has_key('updated_parsed'):
                    feed_time_tuple = time.struct_time(fp.feed.updated_parsed)
                    feed_datetime = datetime.datetime.fromtimestamp(time.mktime(feed_time_tuple))

                    time_since_last_udpate = self.now - feed_datetime
                    if time_since_last_udpate > self.timedelta:
                        print("last update: '{}' ->  '{}'".format(time_since_last_udpate, item))
                else:
                    print("last update unknown: '{}'".format(item))

            self.queue.task_done()

def read_xml_url_from_file(file_name):
    '''read a opml file and return xmlUrl attrib as list.'''
    xml_urls = []
    with open(file_name, 'r') as f:
        tree = ElementTree.parse(f)
        for node in tree.getiterator('outline'):
            url = node.attrib.get('xmlUrl')
            xml_urls.append(url)
    return xml_urls


if __name__ == "__main__":
    xml_queue = Queue.Queue()

    #init Feedcheck
    for i in range(THREADS):
         t = Feedcheck(xml_queue)
         t.setDaemon(True)
         t.start()

    #put urls in there
    for item in read_xml_url_from_file('/home/flo/test.opml'):
        xml_queue.put(item)

    #wait and finish
    xml_queue.join()


# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4 smartindent autoindent 
