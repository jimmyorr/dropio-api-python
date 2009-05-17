#!/usr/bin/env python

"""
Based on http://groups.google.com/group/dropio-api/web/full-api-documentation
"""

__author__ = 'jimmyorr@gmail.com (Jimmy Orr)'

import os.path
import re
from StringIO import StringIO
import urllib
import urllib2

import pycurl
try: import json
except ImportError: import simplejson as json

from resource import Asset, Drop, Link, Note

API_VERSION = '1.0'
API_FORMAT = 'json'

API_BASE_URL = 'http://api.drop.io/'
FILE_UPLOAD_URL = 'http://assets.drop.io/upload'

DROPS = 'drops/'
ASSETS = '/assets/'
COMMENTS = '/comments/'
SEND_TO = '/send_to'

class DropIoClient(object):
    """Client for the Drop.io service."""
    
    def __init__(self, api_key):
        self.__base_params_dict = {}
        self.__base_params_dict['api_key'] = api_key
        self.__base_params_dict['version'] = API_VERSION
        self.__base_params_dict['format'] = API_FORMAT
    
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
    
    def __curl_post(self, url, params_dict):
        # TODO: wish there was a better way to do this...preferably without curl
        def __parse_headers(headers_str):
            cookies_dict = {}
            headers_dict = {}
            
            lines = re.split('\r?\n', headers_str)
            for line in lines:
                try:
                    name, value = line.split(': ', 1)
                    if 'Set-Cookie' == name:
                        match = re.search('^([^=]+)=([^;]+)*', value)
                        if match:
                            cookies_dict[match.group(1)] = match.group(2)
                    else:
                        headers_dict[name] = value
                except ValueError:
                    pass
            
            return headers_dict
    
        c = pycurl.Curl()
        headers = StringIO()
        body = StringIO()
        
        c.setopt(pycurl.HEADERFUNCTION, headers.write)
        c.setopt(pycurl.WRITEFUNCTION, body.write)
        c.setopt(pycurl.URL, str(url))
        c.setopt(pycurl.HTTPPOST, params_dict.items())
        
        c.perform()
        c.close()
        
        headers.seek(0)
        headers_dict = __parse_headers(headers.read())
        headers.close()
        
        body.seek(0)
        body_dict = json.load(body)
        body.close()
        
        if headers_dict.get('Status') != '200 OK':
            response_dict = body_dict.get('response')
            if response_dict and getattr(response_dict, 'get'):
                raise RuntimeError(response_dict.get('message'))
        
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
            
        url = API_BASE_URL + DROPS
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
        
        url = API_BASE_URL + DROPS + drop_name
        drop_dict = self.__get(url, params_dict)
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
            params_dict['guests_can_comment'] = drop.guests_can_comment
        if drop.guests_can_add is not None:
            params_dict['guests_can_add'] = drop.guests_can_add
        if drop.guests_can_delete is not None:
            params_dict['guests_can_delete'] = drop.guests_can_delete
        if drop.expiration_length is not None:
            params_dict['expiration_length'] = drop.expiration_length
        if drop.password is not None:
            params_dict['password'] = drop.password
        if drop.admin_password is not None:
            params_dict['admin_password'] = drop.admin_password
        params_dict.update(self.__base_params_dict)
        
        url = API_BASE_URL + DROPS + drop.name
        drop_dict = self.__put(url, params_dict)
        drop = Drop(drop_dict)
        
        return drop
    
    def delete_drop(self, drop_name, token):
        assert drop_name is not None
        assert token is not None
        
        params_dict = {}
        params_dict['token'] = token
        params_dict.update(self.__base_params_dict)
        
        url = API_BASE_URL + DROPS + drop_name
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
        
        url = API_BASE_URL + DROPS + drop_name + ASSETS
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
        
        url = API_BASE_URL + DROPS + drop_name + ASSETS
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
        params_dict['file'] = (pycurl.FORM_FILE, file_name)
        if token is not None:
            params_dict['token'] = token
        params_dict.update(self.__base_params_dict)
        
        url = FILE_UPLOAD_URL
        asset_dict = self.__curl_post(url, params_dict)
        asset = Asset(asset_dict)
        
        return asset
    
    def get_asset_list(self, drop_name, token=None):
        """
        Returns:
            list of dropio.resource.Asset
        """
        assert drop_name is not None
        
        params_dict = {}
        if token is not None:
            params_dict['token'] = token
        params_dict.update(self.__base_params_dict)
        
        # TODO: paginate through asset list for > 30 assets
        url = API_BASE_URL + DROPS + drop_name + ASSETS
        asset_dicts = self.__get(url, params_dict)
        
        for asset_dict in asset_dicts:
            yield Asset(asset_dict)
    
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
        
        url = API_BASE_URL + DROPS + drop_name + ASSETS + asset_name
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
        
        url = API_BASE_URL + DROPS + drop_name + ASSETS + asset.name
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
        
        url = API_BASE_URL + DROPS + drop_name + ASSETS + asset_name
        self.__delete(url, params_dict)
        
        return
    
    def __send_asset(self, drop_name, asset_name, medium, params_dict, token=None):
        assert drop_name is not None
        assert asset_name is not None
        
        params_dict['medium'] = medium
        if token is not None:
            params_dict['token'] = token
        params_dict.update(self.__base_params_dict)
        
        url = API_BASE_URL + DROPS + drop_name + ASSETS + asset_name + SEND_TO
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
