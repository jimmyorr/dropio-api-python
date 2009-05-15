#!/usr/bin/env python

"""
Based on http://groups.google.com/group/dropio-api/web/full-api-documentation
"""

__author__ = 'jimmyorr@gmail.com (Jimmy Orr)'

from StringIO import StringIO
import os.path
import pycurl
import urllib

try: import json
except ImportError: import simplejson as json

from resource import Asset, Drop, Link

API_VERSION = '1.0'
API_FORMAT = 'json'

API_BASE_URL = 'http://api.drop.io/'
FILE_UPLOAD_URL = 'http://assets.drop.io/upload'

ASSETS = '/assets/'
DROPS = 'drops/'

class DropIoClient(object):
    """Client for the Drop.io service."""
    
    def __init__(self, api_key):
        self.__base_params_dict = {}
        self.__base_params_dict['api_key'] = api_key
        self.__base_params_dict['version'] = API_VERSION
        self.__base_params_dict['format'] = API_FORMAT
    
    def __curl_get(self, base_url, params_dict):
        c = pycurl.Curl()
        buffer = StringIO()
        url = base_url + '?' + urllib.urlencode(params_dict)
        
        c.setopt(pycurl.WRITEFUNCTION, buffer.write)
        c.setopt(pycurl.URL, str(url))
        
        c.perform()
        c.close()
        
        buffer.seek(0)
        json_decoded = json.load(buffer)
        buffer.close()
        
        return json_decoded
    
    def __curl_post(self, url, params_dict):
        c = pycurl.Curl()
        buffer = StringIO()
        
        c.setopt(pycurl.WRITEFUNCTION, buffer.write)
        c.setopt(pycurl.URL, str(url))
        c.setopt(pycurl.HTTPPOST, params_dict.items())
        
        c.perform()
        c.close()
        
        buffer.seek(0)
        json_decoded = json.load(buffer)
        buffer.close()
        
        return json_decoded
    
    def __map_drop(self, drop, dict):
        drop.name = dict.get('name')
        drop.email = dict.get('email')
        drop.voicemail = dict.get('voicemail')
        drop.conference = dict.get('conference')
        drop.fax = dict.get('fax')
        drop.rss = dict.get('rss')
        drop.asset_count = dict.get('asset_count')
        return
    
    def __map_asset(self, asset, dict):
        asset.name = dict.get('name')
        asset.type = dict.get('type')
        asset.title = dict.get('title')
        asset.description = dict.get('description')
        asset.filesize = dict.get('filesize') 
        asset.created_at = dict.get('created_at')
        return
    
    def __map_link(self, link, dict):
        self.__map_asset(link, dict)
        link.url = dict.get('url')
        return
    
    ################
    # DROP RESOURCE
    ################
    
    def create_drop(self, drop_name=None):
        """
        Returns:
            dropio.resource.Drop
        """
        
        params_dict = {}
        if drop_name is not None:
            params_dict['name'] = str(drop_name)
        params_dict.update(self.__base_params_dict)
            
        url = API_BASE_URL + DROPS
        drop_dict = self.__curl_post(url, params_dict)
        
        drop = Drop()
        self.__map_drop(drop, drop_dict)
        
        return drop
    
    def get_drop(self, drop_name, token=None):
        """
        Returns:
            dropio.resource.Drop
        """
        assert drop_name is not None
        
        url = API_BASE_URL + DROPS + drop_name
        
        params_dict = {}
        if token is not None:
            params_dict['token'] = str(token)
        params_dict.update(self.__base_params_dict)
        
        drop_dict = self.__curl_get(url, params_dict)
        
        drop = Drop()
        self.__map_drop(drop, drop_dict)
        
        return drop
    
    def update_drop(self, drop, token=None):
        """
        Returns:
            dropio.resource.Drop
        """
        # TODO: implement me
        raise NotImplementedError()
    
    def delete_drop(self, drop_name, token):
        """
        Returns:
            ???
        """
        # TODO: implement me
        raise NotImplementedError()
    
    
    #################
    # ASSET RESOURCE
    #################
    
    def create_link(self, drop_name, link_url, token=None):
        """
        Returns:
            dropio.resource.Link
        """
        assert drop_name is not None
        assert link_url is not None
        
        params_dict = {}
        params_dict['url'] = str(link_url)
        if token is not None:
            params_dict['token'] = str(token)
        params_dict.update(self.__base_params_dict)
        
        url = API_BASE_URL + DROPS + drop_name + ASSETS
        link_dict = self.__curl_post(url, params_dict)
        
        link = Link()
        self.__map_link(link, link_dict)
        
        return link
    
    def create_note(self, drop_name, contents, title=None, token=None):
        """
        Returns:
            dropio.resource.Asset
        """
        # TODO: implement me
        raise NotImplementedError()
    
    def create_file(self, drop_name, file_name, token=None):
        """
        Returns:
            dropio.resource.Asset
        """
        assert drop_name is not None
        assert file_name is not None
        assert os.path.isfile(file_name) is True
        
        params_dict = {}
        params_dict['drop_name'] = str(drop_name)
        params_dict['file'] = (pycurl.FORM_FILE, str(file_name))
        if token is not None:
            params_dict['token'] = str(token)
        params_dict.update(self.__base_params_dict)
        
        url = FILE_UPLOAD_URL
        asset_dict = self.__curl_post(url, params_dict)
        
        asset = Asset()
        self.__map_asset(asset, asset_dict)
        
        return asset
    
    def get_asset_list(self, drop_name, token=None):
        """
        Returns:
            list of dropio.resource.Asset
        """
        assert drop_name is not None
        
        params_dict = {}
        if token is not None:
            params_dict['token'] = str(token)
        params_dict.update(self.__base_params_dict)
        
        # TODO: paginate through asset list for > 30 assets
        url = API_BASE_URL + DROPS + drop_name + ASSETS
        asset_dicts = self.__curl_get(url, params_dict)
        
        for asset_dict in asset_dicts:
            asset = Asset()
            self.__map_asset(asset, asset_dict)
            yield asset
    
    def get_asset(self, drop_name, asset_name, token=None):
        """
        Returns:
            dropio.resource.Asset
        """
        # TODO: implement me
        raise NotImplementedError()
    
    def update_asset(self, drop_name, asset, token=None):
        """
        Returns:
            dropio.resource.Asset
        """
        # TODO: implement me
        raise NotImplementedError()
    
    def delete_asset(self, drop_name, asset_name, token=None):
        """
        Returns:
            ???
        """
        # TODO: implement me
        raise NotImplementedError()
    
    def send_asset(self, drop_name, asset_name, medium, 
                   emails=None, fax_number=None, token=None):
        """
        Returns:
            ???
        """
        # TODO: implement me
        raise NotImplementedError()
    
    
    ###################
    # COMMENT RESOURCE
    ###################
    
    def get_comment_list(self, drop_name, asset_name, token=None):
        """
        Returns:
            list of dropio.resource.Comment
        """
        # TODO: implement me
        raise NotImplementedError()

    def create_comment(self, drop_name, asset_name, contents, token=None):
        """
        Returns:
            dropio.resource.Comment
        """
        # TODO: implement me
        raise NotImplementedError()
    
    def get_comment(self, drop_name, asset_name, comment_id, token=None):
        """
        Returns:
            dropio.resource.Comment
        """
        # TODO: implement me
        raise NotImplementedError()
    
    def update_comment(self, drop_name, asset_name, comment, token):
        """
        Returns:
            dropio.resource.Comment
        """
        # TODO: implement me
        raise NotImplementedError()
    
    def delete_comment(self, drop_name, asset_name, comment_id, token):
        """
        Returns:
            ???
        """
        # TODO: implement me
        raise NotImplementedError()
