# -*- coding: utf-8 -*-
import sys
import xbmc
import xbmcaddon
import xbmcgui

import json
import gzip 

from urllib.request import urlopen, Request
from urllib.error import HTTPError

import requests

class API:
    def __init__(self):
        self.headers = {'User-Agent' : 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:107.0) Gecko/20100101 Firefox/107.0', 'Accept-Encoding' : 'gzip', 'Accept' : '*/*', 'Content-type' : 'application/json;charset=UTF-8'} 

    def get_headers(self, token, device_id = None):
        addon = xbmcaddon.Addon()
        if device_id is not None:
            if device_id == '':
                xbmcgui.Dialog().notification('Rebit.tv',addon.getLocalizedString(300210), xbmcgui.NOTIFICATION_ERROR, 10000)
                sys.exit() 
            else:
                headers = {'Authorization' : 'Bearer ' + token, 'X-Television-Client-ID' : device_id, 'User-Agent' : 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:107.0) Gecko/20100101 Firefox/107.0', 'Accept-Encoding' : 'gzip', 'Accept' : '*/*', 'Content-type' : 'application/json;charset=UTF-8'} 
        else:
            headers = {'Authorization' : 'Bearer ' + token, 'User-Agent' : 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:107.0) Gecko/20100101 Firefox/107.0', 'Accept-Encoding' : 'gzip', 'Accept' : '*/*', 'Content-type' : 'application/json;charset=UTF-8'} 
        return headers

    def call_api(self, url, data, method, headers):
        addon = xbmcaddon.Addon()
        if data != None:
            data = json.dumps(data).encode("utf-8")
        request = Request(url = url , data = data, method = method, headers = headers)
        if addon.getSetting('log_request_url') == 'true':
            xbmc.log('Rebit.tv > ' + str(url))
        try:
            response = urlopen(request)
            if response.getheader("Content-Encoding") == 'gzip':
                gzipFile = gzip.GzipFile(fileobj = response)
                html = gzipFile.read()
            else:
                html = response.read()
            if addon.getSetting('log_response') == 'true':
                xbmc.log('Rebit.tv > ' + str(html))
            if html and len(html) > 0:
                data = json.loads(html)
                return data
            else:
                return []
        except HTTPError as e:
            xbmc.log('Rebit.tv > ' + addon.getLocalizedString(300204) + str(url) + ': ' + e.reason)
            return { 'err' : e.reason }  

    def call_requests_api(self, url, data, headers):
        addon = xbmcaddon.Addon()
        if addon.getSetting('log_request_url') == 'true':
            xbmc.log('Rebit.tv > ' + str(url))
        try:
            response = requests.post(url = url, json = data, headers = headers)
            data = response.json()
            if addon.getSetting('log_response') == 'true':
                xbmc.log('Rebit.tv > ' + str(data))
            return data
        except Exception as e:
            xbmc.log('Rebit.tv > ' + addon.getLocalizedString(300204) + str(url) + ': ' + e.reason)
            return { 'err' : e.reason }  

