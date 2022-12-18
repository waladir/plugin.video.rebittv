# -*- coding: utf-8 -*-
import sys
import xbmc
import xbmcaddon
import xbmcgui

import json
import time 
from datetime import datetime

from libs.api import API

class Session:
    def __init__(self):
        self.valid_to = -1
        self.load_session()

    def create_session(self):
        self.get_token()

    def get_token(self):
        addon = xbmcaddon.Addon()
        api = API()
        post = {'username' : addon.getSetting('username'), 'password' : addon.getSetting('password')} 
        response = api.call_api(url = 'https://bbxnet.api.iptv.rebit.sk/auth/auth', data = post, method = 'POST', headers = api.headers)
        if 'data' not in response or 'access_token' not in response['data']:
            xbmcgui.Dialog().notification('Rebit.tv',addon.getLocalizedString(300206), xbmcgui.NOTIFICATION_ERROR, 5000)
            sys.exit() 
        self.access_token = response['data']['access_token']
        self.refresh_token = response['data']['refresh_token']
        self.expire_in = response['data']['expire_in']
        self.expires = int(time.time()) + int(self.expire_in) -1
        self.user_id = response['data']['user_id']
        self.device_id = ''
        self.save_session()
        self.register_device()
        self.save_session()

    def refresh_session(self):
        addon = xbmcaddon.Addon()
        api = API()
        response = api.call_api(url = 'https://bbxnet.api.iptv.rebit.sk/auth/auth', data = None, method = 'POST', headers = api.get_headers(self.refresh_token))
        if 'data' not in response or 'access_token' not in response['data']:
            xbmcgui.Dialog().notification('Rebit.tv',addon.getLocalizedString(300206), xbmcgui.NOTIFICATION_ERROR, 5000)
            sys.exit() 
        self.access_token = response['data']['access_token']
        self.refresh_token = response['data']['refresh_token']
        self.expire_in = response['data']['expire_in']
        self.expires = int(time.time()) + int(self.expire_in) - 1
        self.user_id = response['data']['user_id']
        self.save_session()
    
    def get_devices(self):
        devices = {}
        addon = xbmcaddon.Addon()
        api = API()
        response = api.call_api(url = 'https://bbxnet.api.iptv.rebit.sk/television/clients', data = None, method = 'GET', headers = api.get_headers(self.access_token))
        if 'data' not in response:
            xbmcgui.Dialog().notification('Rebit.tv',addon.getLocalizedString(300207), xbmcgui.NOTIFICATION_ERROR, 5000)
            sys.exit() 
        for device in response['data']:
            if device['heartbeat_at'] is None:
                last_activity = 'nikdy'
            else:
                last_activity = datetime.fromtimestamp(device['heartbeat_at']).strftime('%d.%m.%Y %H:%M:%S')
            devices.update({device['id'] : {'title' : device['title'], 'last_activity' : last_activity}})
        return devices

    def delete_device(self, id):
        api = API()
        api.call_api(url = 'https://bbxnet.api.iptv.rebit.sk/television/clients/' + id, data = None, method = 'DELETE', headers = api.get_headers(self.access_token))

    def get_device_title(self):
        addon = xbmcaddon.Addon()
        return 'Kodi ' + xbmc.getInfoLabel('System.BuildVersion').split(' ')[0] + ' - ' + addon.getSetting('device_name') + ' [' + addon.getSetting('device_id') + ']'

    def register_device(self):
        addon = xbmcaddon.Addon()
        title = self.get_device_title()
        devices = self.get_devices()
        for id in devices:
            if devices[id]['title'] == title:
                self.delete_device(id = id)
        post = {'title' : title, 'childLockCode' : '0000', 'type' : 'computer'}
        api = API()
        response = api.call_requests_api(url = 'https://bbxnet.api.iptv.rebit.sk/television/client', data = post, headers = api.get_headers(self.access_token))
        if 'error' in response:
            if response['error'] == 'CLIENT_LIMIT_EXCEEDED':
                xbmcgui.Dialog().notification('Rebit.tv',addon.getLocalizedString(300209), xbmcgui.NOTIFICATION_ERROR, 5000)
                sys.exit() 
            else:
                xbmcgui.Dialog().notification('Rebit.tv',addon.getLocalizedString(300207), xbmcgui.NOTIFICATION_ERROR, 5000)
                sys.exit() 
        if 'data' not in response or 'id' not in response['data']:
            xbmcgui.Dialog().notification('Rebit.tv',addon.getLocalizedString(300207), xbmcgui.NOTIFICATION_ERROR, 5000)
            sys.exit() 
        self.device_id = response['data']['id']

    def heartbeat(self):
        api = API()
        api.call_api(url = 'https://bbxnet.api.iptv.rebit.sk/television/client/heartbeat', data = None, method = 'POST', headers = api.get_headers(self.access_token, self.device_id))

    def load_session(self):
        from libs.settings import Settings
        settings = Settings()
        data = settings.load_json_data({'filename' : 'session.txt', 'description' : 'session'})
        if data is not None:
            data = json.loads(data)
            self.access_token = data['access_token']
            self.refresh_token = data['refresh_token']
            self.user_id = data['user_id']
            self.expires = int(data['expires'])
            self.device_id = data['device_id']
            if self.expires: 
                if self.expires < int(time.time()):
                    self.refresh_session()
            else:
                self.create_session()
            if self.device_id != '':
                self.heartbeat()
        else:
            self.create_session()

    def save_session(self):
        from libs.settings import Settings
        settings = Settings()
        data = json.dumps({'access_token' : self.access_token, 'refresh_token' : self.refresh_token, 'user_id' : self.user_id, 'expires' : self.expires, 'device_id' : self.device_id})
        settings.save_json_data({'filename' : 'session.txt', 'description' : 'session'}, data)

    def remove_session(self):
        from libs.settings import Settings
        addon = xbmcaddon.Addon()
        settings = Settings()
        settings.reset_json_data({'filename' : 'session.txt', 'description' : 'session'})
        self.valid_to = -1
        self.create_session()
        xbmcgui.Dialog().notification('Rebit.tv', addon.getLocalizedString(300205), xbmcgui.NOTIFICATION_INFO, 5000)
