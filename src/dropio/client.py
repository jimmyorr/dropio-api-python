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
        self.api_key = api_key
        self.token = token
        
        params = {}
        params['api_key'] = self.api_key
        params['token'] = self.token 
        params['version'] = API_VERSION
        params['format'] = API_FORMAT
        self.urlencoded_params = urllib.urlencode(params)
    
    def get_asset_list(self, drop_name):
        """
        Returns:
            list of dropio.resource.Asset
        """
        assert drop_name is not None
        
        # TODO: paginate through asset list for > 30 assets
        url = BASE_URL + drop_name + ASSETS + '?' + self.urlencoded_params
        f = self.__urlopen(url)
        
        json_encoded = StringIO(f.read())
        json_decoded = json.load(json_encoded)
        for asset_dict in json_decoded:
            a = Asset(asset_dict.get('url_fragment'),
                      asset_dict.get('asset_type'),
                      asset_dict.get('title'), 
                      asset_dict.get('description'),
                      asset_dict.get('file_size'), 
                      asset_dict.get('created_at')                        
                      )
            yield a
    
    def get_drop(self, drop_name):
        """
        Returns:
            dropio.resource.Drop
        """
        assert drop_name is not None
        
        url = BASE_URL + DROPS + drop_name + '?' + self.urlencoded_params
        f = self.__urlopen(url)
        json_encoded = StringIO(f.read())
        json_decoded = json.load(json_encoded)
        
        d = Drop(json_decoded.get('url'),
                 json_decoded.get('email'),
                 json_decoded.get('voicemail'),
                 json_decoded.get('conference'),
                 json_decoded.get('fax_coverpage_url'),
                 json_decoded.get('rss'),
                 'FIXME: where is asset count?')
        return d

    def __urlopen(self, url):
        try:
            f = urllib2.urlopen(url)
        except IOError:
            raise
        return f