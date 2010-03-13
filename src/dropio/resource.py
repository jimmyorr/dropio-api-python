#!/usr/bin/env python

""" 
Based on http://groups.google.com/group/dropio-api/web/resource-descriptions
"""

__author__ = 'jimmyorr@gmail.com (Jimmy Orr)'

class Resource(object):
    def __init__(self):
        pass


class Drop(Resource):
    def __init__(self, drop_dict):
        assert drop_dict is not None
        
        Resource.__init__(self)
        
        self.name = drop_dict.get('name')
        self.description = drop_dict.get('description')
        self.email = drop_dict.get('email')
        self.voicemail = drop_dict.get('voicemail')
        self.conference = drop_dict.get('conference')
        self.fax = drop_dict.get('fax')
        self.rss = drop_dict.get('rss')
        self.asset_count = drop_dict.get('asset_count')
        self.guest_token = drop_dict.get('guest_token')
        self.admin_token = drop_dict.get('admin_token')
        self.expiration_length = drop_dict.get('expiration_length')
        self.guests_can_comment = drop_dict.get('guests_can_comment')
        self.guests_can_add = drop_dict.get('guests_can_add')
        self.guests_can_delete = drop_dict.get('guests_can_delete')
        self.max_bytes = drop_dict.get('max_bytes')
        self.current_bytes = drop_dict.get('current_bytes')
        self.hidden_upload_url = drop_dict.get('hidden_upload_url')
        
        self.password = drop_dict.get('password')
        self.admin_password = drop_dict.get('admin_password')
    
    def __str__(self):
        return self.name


class Asset(Resource):
    def __init__(self, asset_dict):
        assert asset_dict is not None
        
        Resource.__init__(self)
        
        self.name = asset_dict.get('name')
        self.type = asset_dict.get('type')
        self.title = asset_dict.get('title')
        self.description = asset_dict.get('description')
        self.filesize = asset_dict.get('filesize')
        self.created_at = asset_dict.get('created_at')
    
    def __str__(self):
        return self.name


class Link(Asset):
    def __init__(self, link_dict):
        assert link_dict is not None
        
        Asset.__init__(self, link_dict)
        
        self.url = link_dict.get('url')
    

class Note(Asset):
    def __init__(self, note_dict):
        assert note_dict is not None
        
        Asset.__init__(self, note_dict)
        
        self.contents = note_dict.get('contents')
    
