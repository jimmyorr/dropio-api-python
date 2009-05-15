#!/usr/bin/env python

__author__ = 'jimmyorr@gmail.com (Jimmy Orr)'

import unittest

import dropio.client

api_key = ''
valid_drop_name = ''
invalid_drop_name = 'zzzzzzzzzzzz'

class DropIoClientUnitTest(unittest.TestCase):
    
    def setUp(self):
        self.client = dropio.client.DropIoClient(api_key)
    
    def tearDown(self):
        # No teardown needed
        pass
    
    
    #############
    # get_drop()
    #############
    
    def test_get_drop_valid_drop_name(self):
        drop = self.client.get_drop(valid_drop_name)
        self.assert_(drop is not None)
        self.assertEquals(drop.name, valid_drop_name)
    
    def test_get_drop_invalid_drop_name(self):
        self.assertRaises(Exception, self.client.get_drop, invalid_drop_name)
        
    def test_get_drop_None_drop_name(self):
        self.assertRaises(Exception, self.client.get_drop, None)
        
    def test_get_drop_empty_drop_name(self):
        self.assertRaises(Exception, self.client.get_drop, '')
    
    
    ################
    # create_link()
    ################
    
    def test_create_link(self):
        link_url = 'http://foo.com'
        link = self.client.create_link(valid_drop_name, link_url)
        self.assert_(link is not None)
        self.assertEquals(link.url, link_url)


if __name__ == '__main__':
    unittest.main()
