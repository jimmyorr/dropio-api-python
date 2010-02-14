#!/usr/bin/env python

__author__ = 'jimmyorr@gmail.com (Jimmy Orr)'

import os
import unittest
import urllib2

import dropio.client

valid_drop_name = 'api_python_test'

class DropIoClientTestCase(unittest.TestCase):
    
    def setUp(self):
        self.client = dropio.client.DropIoClient(os.getenv('DROPIO_API_KEY'))
    
    def tearDown(self):
        # No teardown needed
        pass
    
    
    ################
    # create_drop()
    ################
    
    def test_create_drop(self):
        drop = self.client.create_drop()
        self.assert_(drop is not None)
    
    
    #############
    # get_drop()
    #############
    
    def test_get_drop_valid_drop_name(self):
        drop = self.client.get_drop(valid_drop_name)
        self.assert_(drop is not None)
        self.assertEquals(drop.name, valid_drop_name)
    
    def test_get_drop_invalid_drop_name(self):
        self.assertRaises(Exception, self.client.get_drop, '#$!')
        
    def test_get_drop_None_drop_name(self):
        self.assertRaises(Exception, self.client.get_drop, None)
        
    def test_get_drop_empty_drop_name(self):
        self.assertRaises(Exception, self.client.get_drop, '')
    
    
    ###############
    # update_drop()
    ###############
    
    def test_update_drop(self):
        drop = self.client.create_drop()
        self.assert_(drop is not None)
        self.assertEquals(drop.guests_can_delete, True)
        drop.guests_can_delete = False
        self.client.update_drop(drop, drop.admin_token)
        updated_drop = self.client.get_drop(drop.name, drop.admin_token)
        self.assertEquals(updated_drop.guests_can_delete, False)
    
    
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
    
    
    ################
    # create_file()
    ################
    
    def test_create_file(self):
        file_name = 'test_create_file.txt'
        file_handle = open(file_name, 'w')
        file_handle.write('0123456789abcdef')
        file_handle.close()
        
        file = self.client.create_file(valid_drop_name, file_name)
        self.assert_(file is not None)
        self.assertEquals(file.filesize, os.stat(file_name).st_size)
        self.assertEquals(file.title, os.path.basename(file_name))
        
        os.remove(file_name)
    
    def test_create_file_that_starts_with_r(self):
        file_name = '.\\r_test_create_file_that_starts_with_r.txt'
        file_handle = open(file_name, 'w')
        file_handle.write('0123456789abcdef')
        file_handle.close()
        
        file = self.client.create_file(valid_drop_name, file_name)
        self.assert_(file is not None)
        self.assertEquals(file.filesize, os.stat(file_name).st_size)
        self.assertEquals(file.title, os.path.basename(file_name))
        
        os.remove(file_name)
    
    
    ###################
    # get_asset_list()
    ###################
    
    def test_get_asset_list(self):
        drop = self.client.get_drop(valid_drop_name)
        self.assert_(drop is not None)
        assets = self.client.get_asset_list(drop.name)
        self.assert_(assets is not None)
    
    
    #######################
    # get_all_asset_list()
    #######################
    
    def test_get_all_asset_list(self):
        drop = self.client.create_drop()
        self.assert_(drop is not None)
        
        NUMBER_OF_NOTES = 31
        
        for ii in range(0, NUMBER_OF_NOTES):
            note_contents = ii
            self.client.create_note(drop.name, note_contents)
        
        drop = self.client.get_drop(drop.name)
        self.assert_(drop is not None)
        
        assets = self.client.get_all_asset_list(drop.name)
        self.assert_(assets is not None)
        
        count = 0
        for asset in assets: #@UnusedVariable
            count += 1
        self.assert_(count == NUMBER_OF_NOTES)
    
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
        updated_link = self.client.update_asset(valid_drop_name, link)
        self.assertEquals(updated_link.url, link.url)
        self.assertEquals(updated_link.title, link.title)
        self.assertEquals(updated_link.description, link.description)
        
        
    #################
    # delete_asset()
    #################
    
    def test_delete_note(self):
        note_contents = 'this note should be deleted'
        note = self.client.create_note(valid_drop_name, note_contents)
        self.assert_(note is not None)
        self.assertEquals(note.contents, note_contents)
        self.client.delete_asset(valid_drop_name, note.name)
    
    
    ###############
    # send_asset()
    ###############
    
    def test_send_asset_to_email(self):
        link_url = 'http://foo.com'
        link = self.client.create_link(valid_drop_name, link_url)
        self.assert_(link is not None)
        
        self.client.send_asset_to_email(valid_drop_name, link.name, 
                                        valid_drop_name + '@drop.io', 
                                        'hello world')


if __name__ == '__main__':
    #suite = unittest.TestSuite()
    #suite.addTest(DropIoClientTestCase('test_send_asset_to_email'))
    
    suite = unittest.TestLoader().loadTestsFromTestCase(DropIoClientTestCase)
    
    unittest.TextTestRunner(verbosity=2).run(suite)
    