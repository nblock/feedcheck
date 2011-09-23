#!/usr/bin/python2
# -*- coding: utf-8 -*-
'''
File    : feedcheck.py
Author  : Florian Preinstorfer
Contact : nblock [/at\] archlinux DOT us
Date    : 20.09.2011
License : GPLv3

Description : Check availability of feeds from opml or plain input.

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
        self._item = None
        self._response = None
        self._parsed_feed = None

    def run(self):
        while True:
            self._item = self.queue.get()
            self._perform_request()
            
            if self._process_status_code():
                self._parse_feed()
                self._process_max_age()

            self.queue.task_done()

    def _perform_request(self):
        self._response = requests.get(self._item)

    def _parse_feed(self):
        self._parsed_feed = feedparser.parse(self._response)

    def _process_status_code(self):
        '''check for status code other than http 200 and print error messages

        TODO: handle common http status codes: 404/301...
        Returns True if status code is 200, False otherwise.
        '''
        ret_bool = True
        if self._response.status_code != 200:
            print("status code '{}': '{}'".format(self._response.status_code, self._item))
            ret_bool = False
        return ret_bool

    def _process_max_age(self):
        '''check for max age (if available).'''
        #try to get last updated date
        if self._parsed_feed.feed.has_key('updated_parsed') and self._parsed_feed.feed.updated_parsed != None:  
            feed_time_tuple = time.struct_time(self._parsed_feed.feed.updated_parsed)
            feed_datetime = datetime.datetime.fromtimestamp(time.mktime(feed_time_tuple))

            time_since_last_udpate = self.now - feed_datetime
            if time_since_last_udpate > self.max_age:
                print("last update: '{}':  '{}'".format(time_since_last_udpate, self._item))
        else:
            print("last update unknown: '{}'".format(self._item))
       

def get_input_from_file(file_object):
    '''Select either OPML or plain file parsing and return list with urls.'''
    line = file_object.readline()
    file_object.seek(0)
    if line.startswith('<'):
        return read_opml_from_file(file_object)
    else:
        return read_plain_url_from_file(file_object)


def read_opml_from_file(file_object):
    '''Read a opml file and return xmlUrl attrib as list.'''
    opml_urls = []
    with file_object:
        try:
            tree = ElementTree.parse(file_object)
            for node in tree.getiterator('outline'):
                url = node.attrib.get('xmlUrl')
                if url == None:
                    print('Missing xmlUrl-tag in OPML file.')
                    continue
                opml_urls.append(url)
        except ParseError, e:
            print("Could not parse OPML file: '{}'".format(e))
    return opml_urls


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
    parser.add_argument('-f', '--file', type=argparse.FileType('r'), default=sys.stdin, help='The input file in OPML or plain format (default: stdin)')
    args = parser.parse_args()

    main(filename=args.file, max_age=args.age, threads=args.threads)

# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4 smartindent autoindent 
