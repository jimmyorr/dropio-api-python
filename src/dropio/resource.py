#!/usr/bin/env python

""" 
Based on http://groups.google.com/group/dropio-api/web/resource-descriptions
"""

__author__ = 'jimmyorr@gmail.com (Jimmy Orr)'

class Resource(object):
    def __init__(self):
        pass


class Drop(Resource):
    def __init__(self, name=None, email=None, voicemail=None, conference=None, 
                 fax=None, rss=None, asset_count=None, guest_token=None, 
                 admin_token=None, expiration_length=None, 
                 guests_can_comment=None, guests_can_add=None, 
                 guests_can_delete=None, max_bytes=None, current_bytes=None, 
                 hidden_upload_url=None):
        Resource.__init__(self)
        self.name = name
        self.email = email
        self.voicemail = voicemail
        self.conference = conference
        self.fax = fax
        self.rss = rss
    
    def __str__(self):
        return self.name


class Asset(Resource):
    def __init__(self, name=None, type=None, title=None, description=None, 
                 filesize=None, created_at=None):
        Resource.__init__(self)
        self.name = name
        self.type = type
        self.title = title
        self.description = description
        self.filesize = filesize
        self.created_at = created_at
    
    def __str__(self):
        return self.name


class Link(Asset):
    def __init__(self, name=None, type=None, title=None, description=None, 
                 filesize=None, created_at=None, url=None):
        Asset.__init__(self, name, type, title, description, filesize, created_at)
        self.url = url
    
