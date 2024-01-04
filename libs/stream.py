# -*- coding: utf-8 -*-
import sys
import xbmcgui
import xbmcplugin
import xbmcaddon

from libs.session import Session
from libs.api import API
from libs.epg import get_channel_epg

if len(sys.argv) > 1:
    _handle = int(sys.argv[1])

def play_catchup(id, start_ts, end_ts):
    start_ts = int(start_ts)
    end_ts = int(end_ts)
    epg = get_channel_epg(id = id, from_ts = start_ts, to_ts = end_ts + 60*60*12)
    if start_ts in epg:
        play_archive(id = epg[start_ts]['id'], channel_id = id)
    else:
        play_live(id = id)

def play_live(id):
    addon = xbmcaddon.Addon()
    session = Session()
    api = API()
    response = api.call_api(url = 'https://bbxnet.api.iptv.rebit.sk/television/channels/' + id + '/play', data = None, method = 'GET', headers = api.get_headers(session.access_token, session.device_id))
    if 'data' in response and 'link' in response['data'] and response['data']['link']:
        url = response['data']['link']
        list_item = xbmcgui.ListItem(path = url)
        if addon.getSetting('isa') != 'true':
            list_item.setProperty('inputstream', 'inputstream.adaptive')
            list_item.setProperty('inputstream.adaptive.manifest_type', 'hls')
        list_item.setContentLookup(False)       
        xbmcplugin.setResolvedUrl(_handle, True, list_item)
    else:
        xbmcgui.Dialog().notification('Rebit.tv', addon.getLocalizedString(300218), xbmcgui.NOTIFICATION_ERROR, 5000)

def play_archive(id, channel_id):
    addon = xbmcaddon.Addon()
    session = Session()
    api = API()
    response = api.call_api(url = 'https://bbxnet.api.iptv.rebit.sk/television/channels/' + channel_id + '/play/' + id, data = None, method = 'GET', headers = api.get_headers(session.access_token, session.device_id))
    if 'data' in response and 'link' in response['data'] and response['data']['link']:
        url = response['data']['link']
        list_item = xbmcgui.ListItem(path = url)
        if addon.getSetting('isa') != 'true':
            list_item.setProperty('inputstream', 'inputstream.adaptive')
            list_item.setProperty('inputstream.adaptive.manifest_type', 'hls')
        list_item.setContentLookup(False)       
        xbmcplugin.setResolvedUrl(_handle, True, list_item)
    else:
        xbmcgui.Dialog().notification('Rebit.tv', addon.getLocalizedString(300218), xbmcgui.NOTIFICATION_ERROR, 5000)
            
