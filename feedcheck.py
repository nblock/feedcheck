#!/usr/bin/python
# -*- coding: utf-8 -*-
'''
File    : feedcheck.py
Author  : Florian Preinstorfer
Contact : nblock [/at\] archlinux DOT us
Date    : 20.09.2011
License : GPLv3

Description : Check feed availability from an opml file.
'''
from xml.etree import ElementTree
import queue
import threading

THREADS = 2

class Feedcheck(threading.Thread):
    '''Check availability of feeds.'''

    def __init__( self, queue ):
        threading.Thread.__init__(self)
        self.queue = queue

    def run(self):
        while True:
            item = self.queue.get()
            print(item)
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
    xml_queue = queue.Queue()

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
