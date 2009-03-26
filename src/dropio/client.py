from StringIO import StringIO
import simplejson as json
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
        assert drop_name is not None
        
        # TODO: paginate through asset list for > 30 assets
        url = BASE_URL + drop_name + ASSETS + '?' + self.urlencoded_params
        try:
            f = urllib2.urlopen(url)
            json_encoded = StringIO(f.read())
            asset_list = json.load(json_encoded)
        except IOError:
            raise
        
        for asset_dict in asset_list:
            # TODO: JSON returned does not match documentation at
            # http://groups.google.com/group/dropio-api/web/resource-descriptions
            yield Asset(asset_dict.get('name'), asset_dict.get('type'),
                        asset_dict.get('title'), asset_dict.get('description'),
                        asset_dict.get('filesize'), asset_dict.get('created_at')
                        )
    
    def get_drop(self, drop_name):
        assert drop_name is not None
        
        url = BASE_URL + DROPS + drop_name + '?' + self.urlencoded_params
        try:
            f = urllib2.urlopen(url)
            json_encoded = StringIO(f.read())
            drop_dict = json.load(json_encoded)
        except IOError:
            raise
        
        return Drop(drop_dict['url'], drop_dict['id'])
