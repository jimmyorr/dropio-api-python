#!/usr/bin/env python

""" 
Based on http://groups.google.com/group/dropio-api/web/resource-descriptions
"""

__author__ = 'jimmyorr@gmail.com (Jimmy Orr)'

class Resource(object):
    def __init__(self):
        pass


class Drop(Resource):
    def __init__(self, *args, **kwargs):
        Resource.__init__(self)
        self.name = kwargs.get('name')
        self.email = kwargs.get('email')
        self.voicemail = kwargs.get('voicemail')
        self.conference = kwargs.get('conference')
        self.fax = kwargs.get('fax')
        self.rss = kwargs.get('rss')
        self.asset_count = kwargs.get('asset_count')
        self.guest_token = kwargs.get('guest_token')
        self.admin_token = kwargs.get('admin_token')
        self.expiration_length = kwargs.get('expiration_length')
        self.guests_can_comment = kwargs.get('guests_can_comment')
        self.guests_can_add = kwargs.get('guests_can_add')
        self.guests_can_delete = kwargs.get('guests_can_delete')
        self.max_bytes = kwargs.get('max_bytes')
        self.current_bytes = kwargs.get('current_bytes')
        self.hidden_upload_url = kwargs.get('hidden_upload_url')
    
    def __str__(self):
        return self.name


class Asset(Resource):
    def __init__(self, *args, **kwargs):
        Resource.__init__(self)
        self.name = kwargs.get('name')
        self.type = kwargs.get('type')
        self.title = kwargs.get('title')
        self.description = kwargs.get('description')
        self.filesize = kwargs.get('filesize')
        self.created_at = kwargs.get('created_at')
    
    def __str__(self):
        return self.name


class Link(Asset):
    def __init__(self, *args, **kwargs):
        Asset.__init__(self, args, kwargs)
        self.url = kwargs.get('url')
    
