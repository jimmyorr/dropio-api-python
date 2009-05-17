#!/usr/bin/env python

__author__ = 'jimmyorr@gmail.com (Jimmy Orr)'

import unittest
import urllib2

import dropio.client

api_key = ''
valid_drop_name = ''
invalid_drop_name = '$$$'

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
    # update_drop()
    ################
    # FIXME: this is returning HTTPError: HTTP Error 500: Internal Server Error
#===============================================================================
#    def test_update_drop(self):
#        drop = self.client.create_drop()
#        self.assert_(drop is not None)
#        self.assertEquals(drop.guests_can_delete, True)
#        drop.guests_can_delete = False
#        self.client.update_drop(drop, drop.admin_token)
#        updated_drop = self.client.get_drop(drop.name, drop.admin_token)
#        self.assertEquals(updated_drop.guests_can_delete, False)
#===============================================================================
    
    
    ################
    # delete_drop()
    ################
    
    def test_delete_drop(self):
        drop = self.client.create_drop()
        self.assert_(drop is not None)
        self.client.delete_drop(drop.name, drop.admin_token)
        self.assertRaises(urllib2.HTTPError, self.client.get_drop, drop.name, drop.admin_token)
    
    
    ################
    # create_link()
    ################
    
    def test_create_link(self):
        link_url = 'http://foo.com'
        link = self.client.create_link(valid_drop_name, link_url)
        self.assert_(link is not None)
        self.assertEquals(link.url, link_url)
    
    
    ################
    # create_note()
    ################
    
    def test_create_note(self):
        note_contents = 'blah blah blah'
        note = self.client.create_note(valid_drop_name, note_contents)
        self.assert_(note is not None)
        self.assertEquals(note.contents, note_contents)
    
    
    ##############
    # get_asset()
    ##############
    
    def test_get_asset(self):
        note_contents = 'blah blah blah'
        note = self.client.create_note(valid_drop_name, note_contents)
        self.assert_(note is not None)
        self.assertEquals(note.contents, note_contents)
        note = self.client.get_asset(valid_drop_name, note.name)
        self.assert_(note is not None)
        self.assertEquals(note.contents, note_contents)
    
    
    #################
    # update_asset()
    #################
    
    def test_update_link(self):
        link_url = 'http://foo.com'
        link = self.client.create_link(valid_drop_name, link_url)
        self.assert_(link is not None)
        link.url = 'http://bar.com'
        link.title = 'this is a title'
        link.description = 'this is a description'
        self.client.update_asset(valid_drop_name, link)
        
        
    #################
    # delete_asset()
    #################
    
    def test_delete_note(self):
        note_contents = 'this note should be deleted'
        note = self.client.create_note(valid_drop_name, note_contents)
        self.assert_(note is not None)
        self.assertEquals(note.contents, note_contents)
        self.client.delete_asset(valid_drop_name, note.name)


if __name__ == '__main__':
    #unittest.main(DropIoClientUnitTest, 'test_update_drop')
    unittest.main()
    