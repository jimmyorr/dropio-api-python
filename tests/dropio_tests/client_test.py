#!/usr/bin/env python

__author__ = 'jimmyorr@gmail.com (Jimmy Orr)'

import unittest

import dropio.client

api_key = ''
drop_name = ''

class DropIoClient(unittest.TestCase):
    
    def setUp(self):
        self.client = dropio.client.DropIoClient(api_key)
    
    def tearDown(self):
        # No teardown needed
        pass
    
    def test_get_drop(self):
        drop = self.client.get_drop(drop_name)
        self.assert_(drop is not None)
        self.assertEquals(drop.name, drop_name)
    
    def test_create_link(self):
        link_url = 'http://foo.com'
        link = self.client.create_link(drop_name, link_url)
        self.assert_(link is not None)
        self.assertEquals(link.url, link_url)
    
    def test_get_asset_list(self):
        # TODO:
        pass

if __name__ == '__main__':
    unittest.main()
