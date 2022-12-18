# -*- coding: utf-8 -*-
import time
from libs.session import Session
from libs.channels import Channels
from libs.api import API

from datetime import datetime

def get_live_epg():
    session = Session()
    api = API()
    response = api.call_api(url = 'https://bbxnet.api.iptv.rebit.sk/television/programmes/current', data = None, method = 'GET', headers = api.get_headers(session.access_token, session.device_id))    
    if 'data' in response:
        return epg_api(data = response['data'] , key = 'channel_id')
    else:
        return {}

def get_channel_epg(id, from_ts, to_ts):
    session = Session()
    api = API()
    response = api.call_api(url = 'https://bbxnet.api.iptv.rebit.sk/television/channels/' + id + '/programmes?filter[start][ge]=' + datetime.fromtimestamp(from_ts-60*60).strftime('%Y-%m-%dT%H:%M:%S.000Z') + '&filter[start][le]=' + datetime.fromtimestamp(to_ts-60*60).strftime('%Y-%m-%dT%H:%M:%S.000Z'), data = None, method = 'GET', headers = api.get_headers(session.access_token, session.device_id))    
    if 'data' in response:
        return epg_api(data = response['data'] , key = 'startts')
    else:
        return {}

def epg_api(data, key):
    epg = {}
    channels = Channels()
    channels_list = channels.get_channels_list('id', visible_filter = False)            
    for item in data:
        id = item['id']
        channel_id = item['channel_id']
        title = item['title']
        description = item['description']
        startts = item['start']
        endts = item['stop']
        epg_item = {'id' : id, 'title' : title, 'channel_id' : channel_id, 'description' : description, 'startts' : startts, 'endts' : endts}
        if key == 'startts':
            epg.update({startts : epg_item})
        elif key == 'channel_id':
            epg.update({channel_id : epg_item})
        elif key == 'id':
            epg.update({id : epg_item})
        elif key == 'startts_channel_number':
            if channel_id in channels_list:
                epg.update({int(str(startts)+str(channels_list[channel_id]['channel_number']).zfill(5))  : epg_item})
    return epg

def epg_listitem(list_item, epg, logo):
    list_item.setInfo('video', {'mediatype' : 'movie'})
    list_item.setArt({'thumb': logo, 'icon': logo})
    if 'description' in epg and len(epg['description']) > 0:
        list_item.setInfo('video', {'plot': epg['description']})
    return list_item

