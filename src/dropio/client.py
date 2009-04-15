#!/usr/bin/env python

"""
Based on http://groups.google.com/group/dropio-api/web/full-api-documentation
"""

__author__ = 'jimmyorr@gmail.com (Jimmy Orr)'

from StringIO import StringIO
import urllib
import urllib2

import simplejson as json

from resource import Asset, Drop

API_VERSION = '1.0'
API_FORMAT = 'json'
BASE_URL = 'http://drop.io/'
API_BASE_URL = 'http://api.drop.io/'

ASSETS = '/assets/'
DROPS = 'drops/'

class DropIoClient(object):
    """Client for the Drop.io service."""
    
    def __init__(self, api_key, token=None):
        self.__api_key = api_key
        self.__token = token
        
        base_params_dict = {}
        base_params_dict['api_key'] = self.__api_key
        base_params_dict['token'] = self.__token 
        base_params_dict['version'] = API_VERSION
        base_params_dict['format'] = API_FORMAT
        self.__base_params = urllib.urlencode(base_params_dict)
    
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
            
        url = BASE_URL + DROPS
        drop_dict = self.__urlopen_post(url, params)
        
        d = Drop(drop_dict.get('url'),
                 drop_dict.get('email'),
                 drop_dict.get('voicemail'),
                 drop_dict.get('conference'),
                 drop_dict.get('fax_coverpage_url'),
                 drop_dict.get('rss'),
                 'FIXME: where is asset count?')
        return d        
            
    def get_drop(self, drop_name):
        """
        Returns:
            dropio.resource.Drop
        """
        assert drop_name is not None
        
        url = BASE_URL + DROPS + drop_name
        drop_dict = self.__urlopen_get(url, self.__base_params)
        
        d = Drop(drop_dict.get('url'),
                 drop_dict.get('email'),
                 drop_dict.get('voicemail'),
                 drop_dict.get('conference'),
                 drop_dict.get('fax_coverpage_url'),
                 drop_dict.get('rss'),
                 'FIXME: where is asset count?')
        return d


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
        url = BASE_URL + drop_name + ASSETS
        asset_dicts = self.__urlopen_get(url, self.__base_params)
        
        for asset_dict in asset_dicts:
            a = Asset(asset_dict.get('url_fragment'),
                      asset_dict.get('asset_type'),
                      asset_dict.get('title'), 
                      asset_dict.get('description'),
                      asset_dict.get('file_size'), 
                      asset_dict.get('created_at')                        
                      )
            yield a
    