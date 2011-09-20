#!/usr/bin/python2
# -*- coding: utf-8 -*-
'''
File    : tests_feedcheck.py
Author  : Florian Preinstorfer
Contact : nblock [/at\] archlinux DOT us
Date    : 20.09.2011
License : GPLv3

Description : Tests for feedcheck.py
'''

import unittest
import feedcheck
from xml.etree.ElementTree import ParseError

class TestFeedcheck(unittest.TestCase):
    '''Unit tests for Feedcheck'''

    _path_to_opml = 'tests/input/'
    _known_good = ['http://www.schneier.com/blog/index.rdf',
        'http://inj3ct0r.com/rss',
        'http://www.exploit-db.com/rss.php']

    def test_pass_valid_opml(self):
        '''Test if Feedcheck can handle valid OPML input.'''
        f = open(''.join((self._path_to_opml, 'valid.opml')), 'r')
        self.assertEqual(self._known_good, feedcheck.read_xml_url_from_file(f))
        f.close()
    
    def test_pass_invalid_opml(self):
        '''Test if Feedcheck can handle invalid OPML input.'''
        f = open(''.join((self._path_to_opml, 'invalid.opml')), 'r')
        #self.assertRaises(ParseError, feedcheck.read_xml_url_from_file(f))
        #self.assertRaises(ParseError, feedcheck.read_xml_url_from_file(f))
        self.assertEqual([], feedcheck.read_xml_url_from_file(f))
        f.close()

if __name__ == '__main__':
    unittest.main()

# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4 smartindent autoindent 
