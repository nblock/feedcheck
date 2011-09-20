#!/usr/bin/python2
# -*- coding: utf-8 -*-
'''
File    : feedcheck.py
Author  : Florian Preinstorfer
Contact : nblock [/at\] archlinux DOT us
Date    : 20.09.2011
License : GPLv3

Description : Check availability of feeds from an opml file or stdin.

Requirements: python>=2.7, requests, feedparser
'''
from xml.etree import ElementTree
from xml.etree.ElementTree import ParseError
import Queue
import threading
import feedparser
import requests
import time
import datetime
import argparse
import sys

class Feedcheck(threading.Thread):
    '''Check availability of feeds.'''

    def __init__( self, queue, max_age ):
        threading.Thread.__init__(self)
        self.queue = queue
        self.now = datetime.datetime.now()
        self.max_age = datetime.timedelta(days=max_age)

    def run(self):
        while True:
            proceed = True
            item = self.queue.get()
            res = requests.get(item)
            
            #status code other than http 200
            if res.status_code != 200:
                print("status code '{}' -> '{}'".format(res.status_code, item))
                proceed = False
            
            #http 200, proceed
            if proceed:
                fp = feedparser.parse(res.content)

                #try to get last updated date
                if fp.feed.has_key('updated_parsed'):
                    feed_time_tuple = time.struct_time(fp.feed.updated_parsed)
                    feed_datetime = datetime.datetime.fromtimestamp(time.mktime(feed_time_tuple))

                    time_since_last_udpate = self.now - feed_datetime
                    if time_since_last_udpate > self.max_age:
                        print("last update: '{}' ->  '{}'".format(time_since_last_udpate, item))
                else:
                    print("last update unknown: '{}'".format(item))

            self.queue.task_done()


def get_input_from_file(file_object):
    '''Select either OPML or plain file parsing and return list with urls.'''
    line = file_object.readline()
    file_object.seek(0)
    if line.startswith('<'):
        return read_xml_url_from_file(file_object)
    else:
        return read_plain_url_from_file(file_object)


def read_xml_url_from_file(file_object):
    '''read a opml file and return xmlUrl attrib as list.'''
    xml_urls = []
    with file_object:
        try:
            tree = ElementTree.parse(file_object)
            for node in tree.getiterator('outline'):
                url = node.attrib.get('xmlUrl')
                if url == None:
                    print('Missing xmlUrl-tag in OPML file.')
                    continue
                xml_urls.append(url)
        except ParseError, e:
            print("Could not parse OPML file: '{}'".format(e))
    return xml_urls


def read_plain_url_from_file(file_object):
    '''read a plain file and return urls as list.'''
    http_urls = []
    with file_object:
        temp_urls = file_object.readlines()
        for line in temp_urls:
            http_urls.append(line.strip())
    return http_urls


def main(filename, max_age, threads):
    '''set up threads and start work'''
    xml_queue = Queue.Queue()

    #init Feedcheck
    for i in range(threads):
         t = Feedcheck(xml_queue, max_age)
         t.setDaemon(True)
         t.start()

    #put urls in there
    for item in get_input_from_file(filename):
        xml_queue.put(item)

    #wait and finish
    xml_queue.join()


if __name__ == "__main__":
    '''parse arguments'''
    parser = argparse.ArgumentParser(description='Check availability of feeds from an opml file.')
    parser.add_argument('-t', '--threads', type=int, choices=xrange(1, 10), default=2, help='The number of threads to use in parallel (default: 2).')
    parser.add_argument('-a', '--age', type=int, default=365, help='The minimum age in days (default: 365).')
    parser.add_argument('-f', '--file', type=argparse.FileType('r'), default=sys.stdin, help='The OPML input file (default: stdin)')
    args = parser.parse_args()

    main(filename=args.file, max_age=args.age, threads=args.threads)

# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4 smartindent autoindent 
