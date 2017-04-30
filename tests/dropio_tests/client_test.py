#!/usr/bin/env python

import os
import unittest
import urllib2

from dropio.client import *

VALID_DROP_NAME = 'api_python_test'

class DropIoClientTestCase(unittest.TestCase):
    
    def setUp(self):
        self.client = DropIoClient(os.getenv('DROPIO_API_KEY'))
    
    def tearDown(self):
        # No teardown needed
        pass
    
    
    ################
    # create_drop()
    ################
    
    def test_create_drop(self):
        drop = self.client.create_drop()
        self.assert_(drop)
    
    
    #############
    # get_drop()
    #############
    
    def test_get_drop_valid_drop_name(self):
        drop = self.client.get_drop(VALID_DROP_NAME)
        self.assert_(drop)
        self.assertEquals(drop.name, VALID_DROP_NAME)
    
    def test_get_drop_invalid_drop_name(self):
        self.assertRaises(ForbiddenError, self.client.get_drop, '!@#$%^&')
    
    def test_get_drop_None_drop_name(self):
        self.assertRaises(AssertionError, self.client.get_drop, None)
    
    def test_get_drop_empty_drop_name(self):
        self.assertRaises(AssertionError, self.client.get_drop, '')
    
#    def test_get_drop_unauthorized(self):
#        drop = self.client.create_drop()
#        drop.admin_password = 'password'
#        drop = self.client.update_drop(drop, drop.admin_token)
#        drop = self.client.get_drop(drop.name)
#        TODO: admin_password does not get set by update_drop!
#        self.assertRaises(ForbiddenError, self.client.get_drop, drop.name)
    
    
    ###############
    # update_drop()
    ###############
    
    def test_update_drop(self):
        drop = self.client.create_drop()
        self.assert_(drop)
        self.assertEquals(drop.guests_can_delete, True)
        self.assertEquals(drop.expiration_length, ExpirationLengthEnum.ONE_WEEK_FROM_LAST_VIEW)
        drop.guests_can_delete = False
        drop.expiration_length = ExpirationLengthEnum.ONE_MONTH_FROM_NOW
        self.client.update_drop(drop, drop.admin_token)
        updated_drop = self.client.get_drop(drop.name, drop.admin_token)
        self.assertEquals(updated_drop.guests_can_delete, False)
        self.assertEquals(drop.expiration_length, ExpirationLengthEnum.ONE_MONTH_FROM_NOW)
    
    
    ################
    # delete_drop()
    ################
    
    def test_delete_drop(self):
        drop = self.client.create_drop()
        self.assert_(drop)
        self.client.delete_drop(drop.name, drop.admin_token)
        self.assertRaises(ResourceNotFoundError, self.client.get_drop, drop.name, drop.admin_token)
    
    
    ################
    # create_link()
    ################
    
    def test_create_link(self):
        link_url = 'http://foo.com'
        link = self.client.create_link(VALID_DROP_NAME, link_url)
        self.assert_(link)
        self.assertEquals(link.url, link_url)
    
        
    def test_create_empty_link(self):
        link_url = ''
        self.assertRaises(AssertionError, self.client.create_link, VALID_DROP_NAME, link_url)
    
    
    ################
    # create_note()
    ################
    
    def test_create_note(self):
        note_contents = 'blah blah blah'
        note = self.client.create_note(VALID_DROP_NAME, note_contents)
        self.assert_(note)
        self.assertEquals(note.contents, note_contents)
    
    def test_create_empty_note(self):
        note_contents = ''
        self.assertRaises(AssertionError, self.client.create_note, VALID_DROP_NAME, note_contents)
    
    ################
    # create_file()
    ################
    
    def test_create_file(self):
        file_name = 'test_create_file.txt'
        file_handle = open(file_name, 'w')
        file_handle.write('0123456789abcdef')
        file_handle.close()
        
        file = self.client.create_file(VALID_DROP_NAME, file_name)
        self.assert_(file)
        self.assertEquals(file.filesize, os.stat(file_name).st_size)
        self.assertEquals(file.title, os.path.basename(file_name))
        
        os.remove(file_name)
    
    def test_create_file_that_starts_with_r(self):
        file_name = 'r_test_create_file_that_starts_with_r.txt'
        file_handle = open(file_name, 'w')
        file_handle.write('0123456789abcdef')
        file_handle.close()
        
        file = self.client.create_file(VALID_DROP_NAME, file_name)
        self.assert_(file)
        self.assertEquals(file.filesize, os.stat(file_name).st_size)
        self.assertEquals(file.title, os.path.basename(file_name))
        
        os.remove(file_name)
   
    def test_create_file_that_does_not_exist(self):
        file_name = 'some_file_that_does_not_exist.txt'
        self.assertRaises(AssertionError, self.client.create_file, VALID_DROP_NAME, file_name)
    
    ###################
    # get_asset_list()
    ###################
    
    def test_get_asset_list(self):
        drop = self.client.get_drop(VALID_DROP_NAME)
        self.assert_(drop)
        assets = self.client.get_asset_list(drop.name)
        self.assert_(assets)
    
    
    #######################
    # get_all_asset_list()
    #######################
    
    def test_get_all_asset_list(self):
        drop = self.client.create_drop()
        self.assert_(drop)
        
        NUMBER_OF_NOTES = 31
        
        for ii in range(0, NUMBER_OF_NOTES):
            note_contents = str(ii)
            self.client.create_note(drop.name, note_contents)
        
        drop = self.client.get_drop(drop.name)
        self.assert_(drop)
        
        assets = self.client.get_all_asset_list(drop.name)
        self.assert_(assets)
        
	assets = list(assets) 
        
        self.assert_(len(assets) == NUMBER_OF_NOTES)
    
    ##############
    # get_asset()
    ##############
    
    def test_get_asset(self):
        note_contents = 'blah blah blah'
        note = self.client.create_note(VALID_DROP_NAME, note_contents)
        self.assert_(note)
        self.assertEquals(note.contents, note_contents)
        note = self.client.get_asset(VALID_DROP_NAME, note.name)
        self.assert_(note)
        self.assertEquals(note.contents, note_contents)
    
    
    #################
    # update_asset()
    #################
    
    def test_update_link(self):
        link_url = 'http://foo.com'
        link = self.client.create_link(VALID_DROP_NAME, link_url)
        self.assert_(link)
        link.url = 'http://bar.com'
        link.title = 'this is a title'
        link.description = 'this is a description'
        updated_link = self.client.update_asset(VALID_DROP_NAME, link)
        self.assertEquals(updated_link.url, link.url)
        self.assertEquals(updated_link.title, link.title)
        self.assertEquals(updated_link.description, link.description)
        
        
    #################
    # delete_asset()
    #################
    
    def test_delete_note(self):
        note_contents = 'this note should be deleted'
        note = self.client.create_note(VALID_DROP_NAME, note_contents)
        self.assert_(note)
        self.assertEquals(note.contents, note_contents)
        self.client.delete_asset(VALID_DROP_NAME, note.name)
    
    
    ###############
    # send_asset()
    ###############
    
    def test_send_asset_to_email(self):
        link_url = 'http://foo.com'
        link = self.client.create_link(VALID_DROP_NAME, link_url)
        self.assert_(link)
        
        self.client.send_asset_to_email(VALID_DROP_NAME, link.name, 
                                        VALID_DROP_NAME + '@drop.io', 
                                        'hello world')


if __name__ == '__main__':
    #suite = unittest.TestSuite()
    #suite.addTest(DropIoClientTestCase('test_get_all_asset_list'))
    
    suite = unittest.TestLoader().loadTestsFromTestCase(DropIoClientTestCase)
    
    unittest.TextTestRunner(verbosity=2).run(suite)
    
