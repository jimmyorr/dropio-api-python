#!/usr/bin/env python

"""
Based on http://groups.google.com/group/dropio-api/web/full-api-documentation
"""

__author__ = 'jimmyorr@gmail.com (Jimmy Orr)'

from StringIO import StringIO
import urllib
import urllib2
import pycurl

try: import json
except ImportError: import simplejson as json

from resource import Asset, Drop

API_VERSION = '1.0'
API_FORMAT = 'json'
BASE_URL = 'http://drop.io/'
API_BASE_URL = 'http://api.drop.io/'
FILE_UPLOAD_URL = 'http://assets.drop.io/upload'

ASSETS = '/assets/'
DROPS = 'drops/'

class DropIoClient(object):
    """Client for the Drop.io service."""
    
    def __init__(self, api_key, token=None):
        self.__api_key = api_key
        self.__token = token
        
        self.__base_params_dict = {}
        self.__base_params_dict['api_key'] = self.__api_key
        self.__base_params_dict['version'] = API_VERSION
        self.__base_params_dict['format'] = API_FORMAT
        if token is not None:
            self.__base_params_dict['token'] = self.__token 
        self.__base_params = urllib.urlencode(self.__base_params_dict)
    
    def __urlopen_get(self, base_url, params):
        try:
            url = base_url + '?' + params
            f = urllib2.urlopen(url)
        except IOError:
            raise
        
        json_encoded = StringIO(f.read())
        json_decoded = json.load(json_encoded)
        
        return json_decoded
    
    def __urlopen_post(self, url, params):
        try:
            f = urllib2.urlopen(url, params)
        except IOError:
            raise
        
        json_encoded = StringIO(f.read())
        json_decoded = json.load(json_encoded)
        
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
            params_dict['name'] = drop_name
        params = self.__base_params + '&' + urllib.urlencode(params_dict)
            
        url = API_BASE_URL + DROPS
        drop_dict = self.__urlopen_post(url, params)
        
        drop = Drop()
        self.__map_drop(drop, drop_dict)
        
        return drop
            
    def get_drop(self, drop_name):
        """
        Returns:
            dropio.resource.Drop
        """
        assert drop_name is not None
        
        url = API_BASE_URL + DROPS + drop_name
        drop_dict = self.__urlopen_get(url, self.__base_params)
        
        drop = Drop()
        self.__map_drop(drop, drop_dict)
        
        return drop


    #################
    # ASSET RESOURCE
    #################
    
    def get_asset_list(self, drop_name):
        """
        Returns:
            list of dropio.resource.Asset
        """
        assert drop_name is not None
        
        # TODO: paginate through asset list for > 30 assets
        url = API_BASE_URL + DROPS + drop_name + ASSETS
        asset_dicts = self.__urlopen_get(url, self.__base_params)
        
        for asset_dict in asset_dicts:
            asset = Asset()
            self.__map_asset(asset, asset_dict)
            yield asset
    
    def create_link(self, drop_name, link_url):
        """
        Returns:
            dropio.resource.Asset
        """
        assert drop_name is not None
        assert link_url is not None
        
        params_dict = {}
        params_dict['url'] = link_url
        params = self.__base_params + '&' + urllib.urlencode(params_dict)
        
        url = API_BASE_URL + DROPS + drop_name + ASSETS
        asset_dict = self.__urlopen_post(url, params)
        
        asset = Asset()
        self.__map_asset(asset, asset_dict)
        
        return asset
    
    def create_file(self, drop_name, file_name):
        assert drop_name is not None
        assert file_name is not None
        
        params_dict = {}
        params_dict['drop_name'] = drop_name
        params_dict['file'] = (pycurl.FORM_FILE, file_name)
        params_dict.update(self.__base_params_dict)
        
        curl = pycurl.Curl()
        buffer = StringIO()
        
        curl.setopt(pycurl.WRITEFUNCTION, buffer.write)
        curl.setopt(pycurl.URL, FILE_UPLOAD_URL)
        curl.setopt(pycurl.HTTPPOST, params_dict.items())    
        
        curl.perform()
        curl.close()
        
        buffer.seek(0) # TODO: why is this needed?
        asset_dict = json.load(buffer)
        buffer.close()
        
        asset = Asset()
        self.__map_asset(asset, asset_dict)
        
        return asset
    
