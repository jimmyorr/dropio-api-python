#!/usr/bin/env python

"""
Based on http://groups.google.com/group/dropio-api/web/full-api-documentation
"""

__author__ = 'jimmyorr@gmail.com (Jimmy Orr)'
__version__ = '0.1'

import httplib
import logging
import mimetypes
import mimetools
import os.path
import sys
import urllib
import urllib2
from optparse import OptionParser
from urlparse import urlsplit

try: import json
except ImportError: import simplejson as json

from dropio.resource import Asset, Drop, Link, Note

_API_VERSION = '2.0'
_API_FORMAT = 'json'

_API_BASE_URL = 'http://api.drop.io/'
_FILE_UPLOAD_URL = 'http://assets.drop.io/upload'

_DROPS = 'drops/'
_ASSETS = '/assets/'
_COMMENTS = '/comments/'
_SEND_TO = '/send_to'

_DROPIO_TRUE = 'true'
_DROPIO_FALSE = 'false'


#########################################################################
# HTTP ERRORS: from http://dev.drop.io/rest-api-reference/response-codes/
#########################################################################

# TODO: consider having these inherit from urllib2.HTTPError

class Error(Exception):
    pass

class BadRequestError(Error):
    """400 Bad Request
    Something is wrong with the request in general (i.e. missing parameters, 
    bad data, etc). 
    """
    pass

class InternalServerError(Error):
    """500 Internal Server Error
    Something that [drop.io] did not account for has gone wrong.
    """
    pass

class ForbiddenError(Error):
    """403 Forbidden
    You did not supply a valid API token or an authorization token.
    """ 
    pass

class ResourceNotFoundError(Error):
    """404 Not Found
    The resource requested is not found or not available.
    """
    pass


class ExpirationLengthEnum(object):
    ONE_DAY_FROM_NOW = '1_DAY_FROM_NOW'
    ONE_WEEK_FROM_NOW = '1_WEEK_FROM_NOW'
    ONE_MONTH_FROM_NOW = '1_MONTH_FROM_NOW'
    ONE_YEAR_FROM_NOW = '1_YEAR_FROM_NOW'
    ONE_DAY_FROM_LAST_VIEW = '1_DAY_FROM_LAST_VIEW'
    ONE_WEEK_FROM_LAST_VIEW = '1_WEEK_FROM_LAST_VIEW'
    ONE_MONTH_FROM_LAST_VIEW = '1_MONTH_FROM_LAST_VIEW'
    ONE_YEAR_FROM_LAST_VIEW = '1_YEAR_FROM_LAST_VIEW'
    
    valid_expiration_lengths = frozenset((ONE_DAY_FROM_NOW,
                                          ONE_WEEK_FROM_NOW,
                                          ONE_MONTH_FROM_NOW,
                                          ONE_YEAR_FROM_NOW,
                                          ONE_DAY_FROM_LAST_VIEW,
                                          ONE_WEEK_FROM_LAST_VIEW,
                                          ONE_MONTH_FROM_LAST_VIEW,
                                          ONE_YEAR_FROM_LAST_VIEW))


class _NullHandler(logging.Handler):
    """default logger does nothing"""
    def emit(self, record):
        pass


class DropIoClient(object):
    """Client for the Drop.io service."""
    
    def __init__(self, api_key, logger=None):
        self.__base_params_dict = {}
        self.__base_params_dict['api_key'] = api_key
        self.__base_params_dict['version'] = _API_VERSION
        self.__base_params_dict['format'] = _API_FORMAT
        if logger:
            self.logger = logger
        else:
            h = _NullHandler()
            self.logger = logging.getLogger()
            self.logger.addHandler(h)
    
    def __get(self, base_url, params_dict):
        params = urllib.urlencode(params_dict)
        f = urllib2.urlopen(base_url + '?' + params)
        body_dict = json.load(f)
        f.close()
        return body_dict
    
    def __post(self, url, params_dict):
        params = urllib.urlencode(params_dict)
        f = urllib2.urlopen(url, params)
        body_dict = json.load(f)
        f.close()
        return body_dict
    
    def __post_multipart(self, url, params_dict):
        def encode_multipart_formdata(params_dict):
            BOUNDARY = mimetools.choose_boundary()
            
            body = ''
            
            for key, value in params_dict.iteritems():
                if isinstance(value, tuple):
                    filename, value = value
                    body += '--%s\r\n' % BOUNDARY
                    body += 'Content-Disposition: form-data;'
                    body += 'name="%s";' % str(key)
                    body += 'filename="%s"\r\n' % str(filename)
                    body += 'Content-Type: %s\r\n\r\n' % str(get_content_type(filename))
                    body += '%s\r\n' % str(value)
                else:
                    body += '--%s\r\n' % BOUNDARY
                    body += 'Content-Disposition: form-data; name="%s"\r\n\r\n' % str(key)
                    body += '%s\r\n' % str(value)
            
            body += '--%s--\r\n' % BOUNDARY
            content_type = 'multipart/form-data; boundary=%s' % BOUNDARY
        
            return body, content_type
        
        def get_content_type(filename):
            return mimetypes.guess_type(filename)[0] or 'application/octet-stream'
        
        body, content_type = encode_multipart_formdata(params_dict)
        headers = {'content-type': content_type}
        
        url_parts = urlsplit(url)
        h = httplib.HTTPConnection(url_parts.netloc)
        h.request('POST', url_parts.path, body, headers)
        response = h.getresponse()
        body_dict = json.load(response)
        h.close()
        return body_dict
    
    def __put(self, url, params_dict):
        opener = urllib2.build_opener(urllib2.HTTPHandler)
        request = urllib2.Request(url, data=json.dumps(params_dict))
        request.add_header('Content-Type', 'application/json')
        request.get_method = lambda: 'PUT'
        f = opener.open(request)
        body_dict = json.load(f)
        f.close()
        opener.close()
        return body_dict
    
    def __delete(self, url, params_dict):
        opener = urllib2.build_opener(urllib2.HTTPHandler)
        request = urllib2.Request(url, data=json.dumps(params_dict))
        request.add_header('Content-Type', 'application/json')
        request.get_method = lambda: 'DELETE'
        f = opener.open(request)
        body_dict = json.load(f)
        f.close()
        opener.close()
        return body_dict
    
    def __asset_dict_to_asset(self, asset_dict):
        # TODO: this isn't ideal...
        asset = None
        if asset_dict.has_key('contents'):
            asset = Note(asset_dict)
        elif asset_dict.has_key('url'):
            asset = Link(asset_dict)
        else:
            asset = Asset(asset_dict)
        return asset
    
    
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
        params_dict.update(self.__base_params_dict)
            
        url = _API_BASE_URL + _DROPS
        drop_dict = self.__post(url, params_dict)
        drop = Drop(drop_dict)
        
        return drop
    
    def get_drop(self, drop_name, token=None):
        """
        Returns:
            dropio.resource.Drop
        """
        assert drop_name is not None
        
        params_dict = {}
        if token is not None:
            params_dict['token'] = token
        params_dict.update(self.__base_params_dict)
        
        url = _API_BASE_URL + _DROPS + drop_name
        try:
            drop_dict = self.__get(url, params_dict)
        except urllib2.HTTPError, e:
            # TODO: move this into reusable method
            if e.code == 400:
                raise BadRequestError()
            elif e.code == 403:
                raise ForbiddenError()
            if e.code == 404:
                raise ResourceNotFoundError()
            if e.code == 500:
                raise ResourceNotFoundError()
            else:
                raise e
        drop = Drop(drop_dict)
        
        return drop
    
    def update_drop(self, drop, token):
        """
        Returns:
            dropio.resource.Drop
        """
        assert drop is not None
        assert token is not None
        
        params_dict = {}
        params_dict['token'] = token
        if drop.guests_can_comment is not None:
            if drop.guests_can_comment:
                params_dict['guests_can_comment'] = _DROPIO_TRUE
            else:
                params_dict['guests_can_comment'] = _DROPIO_FALSE
        if drop.guests_can_add is not None:
            if drop.guests_can_add:
                params_dict['guests_can_add'] = _DROPIO_TRUE
            else:
                params_dict['guests_can_add'] = _DROPIO_FALSE
        if drop.guests_can_delete is not None:
            if drop.guests_can_delete:
                params_dict['guests_can_delete'] = _DROPIO_TRUE
            else:
                params_dict['guests_can_delete'] = _DROPIO_FALSE
        if drop.expiration_length is not None:
            params_dict['expiration_length'] = drop.expiration_length
        if drop.password is not None:
            params_dict['password'] = drop.password
        if drop.admin_password is not None:
            params_dict['admin_password'] = drop.admin_password
        params_dict.update(self.__base_params_dict)
        
        url = _API_BASE_URL + _DROPS + drop.name
        drop_dict = self.__put(url, params_dict)
        drop = Drop(drop_dict)
        
        return drop
    
    def delete_drop(self, drop_name, token):
        assert drop_name is not None
        assert token is not None
        
        params_dict = {}
        params_dict['token'] = token
        params_dict.update(self.__base_params_dict)
        
        url = _API_BASE_URL + _DROPS + drop_name
        self.__delete(url, params_dict)
        
        return
    
    #################
    # ASSET RESOURCE
    #################
    
    def create_link(self, drop_name, link_url, 
                    title=None, description=None, token=None):
        """
        Returns:
            dropio.resource.Link
        """
        assert drop_name is not None
        assert link_url is not None
        
        params_dict = {}
        params_dict['url'] = link_url
        if title is not None:
            params_dict['title'] = title
        if description is not None:
            params_dict['description'] = description
        if token is not None:
            params_dict['token'] = token
        params_dict.update(self.__base_params_dict)
        
        url = _API_BASE_URL + _DROPS + drop_name + _ASSETS
        link_dict = self.__post(url, params_dict)
        link = Link(link_dict)
        
        return link
    
    def create_note(self, drop_name, contents, title=None, token=None):
        """
        Returns:
            dropio.resource.Note
        """
        assert drop_name is not None
        assert contents is not None
        
        params_dict = {}
        params_dict['contents'] = contents
        if title is not None:
            params_dict['title'] = title
        if token is not None:
            params_dict['token'] = token
        params_dict.update(self.__base_params_dict)
        
        url = _API_BASE_URL + _DROPS + drop_name + _ASSETS
        note_dict = self.__post(url, params_dict)
        note = Note(note_dict)
        
        return note
    
    def create_file(self, drop_name, file_name, token=None):
        """
        Returns:
            dropio.resource.Asset
        """
        assert drop_name is not None
        assert file_name is not None
        assert os.path.isfile(file_name) is True
        
        params_dict = {}
        params_dict['drop_name'] = drop_name
        if token is not None:
            params_dict['token'] = token
        input = open(file_name, 'rb')
        params_dict['file'] = (file_name, input.read())
        input.close()
        params_dict.update(self.__base_params_dict)
        
        url = _FILE_UPLOAD_URL
        
        asset_dict = self.__post_multipart(url, params_dict)
        asset = Asset(asset_dict)
        
        return asset
    
    def get_asset_list(self, drop_name, page=1, token=None):
        """
        Returns:
            generator of dropio.resource.Asset
        """
        assert drop_name is not None
        
        params_dict = {}
        params_dict['page'] = page
        if token is not None:
            params_dict['token'] = token
        params_dict.update(self.__base_params_dict)
        
        url = _API_BASE_URL + _DROPS + drop_name + _ASSETS
        response = self.__get(url, params_dict)
        
        for asset_dict in response['assets']:
            yield Asset(asset_dict)
        
        return
    
    def get_all_asset_list(self, drop_name, token=None):
        """
        Returns:
            generator of dropio.resource.Asset
        """
        assert drop_name is not None
        
        page = 1
        while True:
            assets = self.get_asset_list(drop_name, page, token)
            empty = True
            for asset in assets:
                yield asset
                empty = False
            if empty:
                break
            page += 1
        
        return
    
    def get_asset(self, drop_name, asset_name, token=None):
        """
        Returns:
            dropio.resource.Asset
        """
        assert drop_name is not None
        assert asset_name is not None
        
        params_dict = {}
        if token is not None:
            params_dict['token'] = token
        params_dict.update(self.__base_params_dict)
        
        url = _API_BASE_URL + _DROPS + drop_name + _ASSETS + asset_name
        asset_dict = self.__get(url, params_dict)
        asset = self.__asset_dict_to_asset(asset_dict)
        
        return asset
    
    def update_asset(self, drop_name, asset, token=None):
        """
        Returns:
            dropio.resource.Asset
        """
        assert drop_name is not None
        assert asset is not None
        
        params_dict = {}
        if token is not None:
            params_dict['token'] = token
        if asset.title is not None:
            params_dict['title'] = asset.title
        if asset.description is not None:
            params_dict['description'] = asset.description
        if hasattr(asset, 'url') and asset.url is not None:
            params_dict['url'] = asset.url
        if hasattr(asset, 'contents') and asset.contents is not None:
            params_dict['contents'] = asset.contents
        params_dict.update(self.__base_params_dict)
        
        url = _API_BASE_URL + _DROPS + drop_name + _ASSETS + asset.name
        asset_dict = self.__put(url, params_dict)
        asset = self.__asset_dict_to_asset(asset_dict)
        
        return asset
    
    def delete_asset(self, drop_name, asset_name, token=None):
        assert drop_name is not None
        assert asset_name is not None
        
        params_dict = {}
        if token is not None:
            params_dict['token'] = token
        params_dict.update(self.__base_params_dict)
        
        url = _API_BASE_URL + _DROPS + drop_name + _ASSETS + asset_name
        self.__delete(url, params_dict)
        
        return
    
    def __send_asset(self, drop_name, asset_name, medium, params_dict, token=None):
        assert drop_name is not None
        assert asset_name is not None
        
        params_dict['medium'] = medium
        if token is not None:
            params_dict['token'] = token
        params_dict.update(self.__base_params_dict)
        
        url = _API_BASE_URL + _DROPS + drop_name + _ASSETS + asset_name + _SEND_TO
        self.__post(url, params_dict)
        
        return
    
    def send_asset_to_fax(self, drop_name, asset_name, fax_number, token=None):
        assert fax_number is not None
        
        params_dict = {}
        params_dict['fax_number'] = fax_number
        self.__send_asset(drop_name, asset_name, 'fax', params_dict, token)
        
        return
        
    def send_asset_to_drop(self, drop_name, asset_name, drop_name_dest, token=None):
        assert drop_name_dest is not None
        
        params_dict = {}
        params_dict['drop_name'] = drop_name_dest
        self.__send_asset(drop_name, asset_name, 'drop', params_dict, token)
        
        return
        
    def send_asset_to_email(self, drop_name, asset_name, emails, message=None, token=None):
        assert emails is not None
        
        params_dict = {}
        params_dict['emails'] = emails
        if message is not None:
            params_dict['message'] = message
        self.__send_asset(drop_name, asset_name, 'email', params_dict, token)
        
        return
    
    
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


def main(argv=None):
    usage = "usage: %prog [options]"
    parser = OptionParser(usage, version="%prog " + __version__)
    
    parser.add_option("-k", "--key", 
                      action="store", dest="api_key",
                      help="REQUIRED! get key from http://api.drop.io/")
    parser.add_option("-v", "--verbose", 
                      action="count", dest="verbosity", default=0)
    parser.add_option("-d", "--drop_name", 
                      action="store", dest="drop_name",
                      metavar="DROP")
    parser.add_option("-t", "--token",
                      action="store", dest="token")
    parser.add_option("-f", "--file", 
                      action="append", dest="files_to_create", default=[],
                      metavar="FILE")
    parser.add_option("-l", "--link",
                      action="append", dest="links_to_create", default=[],
                      metavar="LINK")
    parser.add_option("-n", "--note",
                      action="append", dest="notes_to_create", default=[],
                      metavar="NOTE")
    (options, unused_args) = parser.parse_args()
    
    assert options.api_key is not None
    
    logger = logging.getLogger()
    logging_level = logging.WARNING - (options.verbosity * 10)
    logger.setLevel(logging_level)
    ch = logging.StreamHandler()
    ch.setLevel(logging_level)
    logger.addHandler(ch)
    
    client = DropIoClient(options.api_key, logger)
    
    try:
        drop = client.get_drop(options.drop_name, options.token)
    except Exception: # TODO: fix diaper anti-pattern
        drop = client.create_drop(options.drop_name)
    
    for file_to_create in options.files_to_create:
        logger.info("Adding file %s to drop %s" % (file_to_create, drop.name))
        client.create_file(drop.name, file_to_create, options.token)
    
    for link_to_create in options.links_to_create:
        logger.info("Adding link '%s' to drop %s" % (link_to_create, drop.name))
        client.create_link(drop.name, link_to_create, options.token)
    
    for note_to_create in options.notes_to_create:
        logger.info("Adding %s to drop %s" % (note_to_create, drop.name))
        client.create_note(drop.name, note_to_create, options.token)


if __name__ == "__main__":
    sys.exit(main())
