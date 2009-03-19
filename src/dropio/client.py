from StringIO import StringIO
import simplejson
import urllib
import urllib2

from resource import Asset
from resource import Drop

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
        # todo: paginate through asset list for > 30 assets
        url = BASE_URL + drop_name + ASSETS + '?' + self.urlencoded_params
        f = urllib2.urlopen(url)
        json_encoded = StringIO(f.read())
        asset_list = simplejson.load(json_encoded)
        for asset_dict in asset_list:
            yield Asset(asset_dict['title'])
    
    def get_drop(self, drop_name):
        url = BASE_URL + DROPS + drop_name + '?' + self.urlencoded_params
        f = urllib2.urlopen(url)
        json_encoded = StringIO(f.read())
        drop_dict = simplejson.load(json_encoded)
        return Drop(drop_dict['url'], drop_dict['id'])
