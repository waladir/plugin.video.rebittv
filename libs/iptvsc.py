# -*- coding: utf-8 -*-
import sys

import xbmcgui
import xbmcaddon
import xbmcvfs

from datetime import datetime
import time

from libs.channels import Channels
from libs.utils import plugin_id
from libs.epg import get_channel_epg

tz_offset = int((time.mktime(datetime.now().timetuple())-time.mktime(datetime.utcnow().timetuple()))/3600)

def save_file_test():
    addon = xbmcaddon.Addon()  
    try:
        content = ''
        output_dir = addon.getSetting('output_dir')      
        test_file = output_dir + 'test.fil'
        file = xbmcvfs.File(test_file, 'w')
        file.write(bytearray(('test').encode('utf-8')))
        file.close()
        file = xbmcvfs.File(test_file, 'r')
        content = file.read()
        if len(content) > 0 and content == 'test':
            file.close()
            xbmcvfs.delete(test_file)
            return 1  
        file.close()
        xbmcvfs.delete(test_file)
        return 0
    except Exception:
        file.close()
        xbmcvfs.delete(test_file)
        return 0 

def generate_playlist(output_file = ''):
    addon = xbmcaddon.Addon()
    if addon.getSetting('output_dir') is None or len(addon.getSetting('output_dir')) == 0:
        xbmcgui.Dialog().notification('Rebit.tv', addon.getLocalizedString(300312), xbmcgui.NOTIFICATION_ERROR, 5000)
        sys.exit() 
             
    channels = Channels()
    channels_list = channels.get_channels_list('channel_number')

    if len(output_file) > 0:
        filename = output_file
    else:
        filename = addon.getSetting('output_dir') + 'playlist.m3u'

    if save_file_test() == 0:
        xbmcgui.Dialog().notification('Rebit.tv', addon.getLocalizedString(300313), xbmcgui.NOTIFICATION_ERROR, 5000)
        return
    try:
        file = xbmcvfs.File(filename, 'w')
        if file == None:
            xbmcgui.Dialog().notification('Rebit.tv', addon.getLocalizedString(300313), xbmcgui.NOTIFICATION_ERROR, 5000)
        else:
            file.write(bytearray(('#EXTM3U\n').encode('utf-8')))
            for number in sorted(channels_list.keys()):  
                logo = channels_list[number]['logo']
                if logo is None:
                    logo = ''
                if addon.getSetting('catchup_mode') == 'default':
                    line = '#EXTINF:-1 catchup="default" catchup-days="7" catchup-source="plugin://plugin.video.rebit.tv/?action=iptsc_play_stream&id=' + str(channels_list[number]['id']) + '&catchup_start_ts={utc}&catchup_end_ts={utcend}" tvg-chno="' + str(number) + '" tvg-id="' + channels_list[number]['name'] + '" tvh-epg="0" tvg-logo="' + logo + '",' + channels_list[number]['name']
                else:
                    line = '#EXTINF:-1 catchup="append" catchup-days="7" catchup-source="&catchup_start_ts={utc}&catchup_end_ts={utcend}" tvg-chno="' + str(number) + '" tvg-id="' + channels_list[number]['name'] + '" tvh-epg="0" tvg-logo="' + logo + '",' + channels_list[number]['name']
                file.write(bytearray((line + '\n').encode('utf-8')))
                line = 'plugin://' + plugin_id + '/?action=iptsc_play_stream&id=' + str(channels_list[number]['id'])
                if addon.getSetting('isa') == 'true':
                    file.write(bytearray(('#KODIPROP:inputstream=inputstream.ffmpegdirect\n').encode('utf-8')))
                    file.write(bytearray(('#KODIPROP:inputstream.ffmpegdirect.stream_mode=timeshift\n').encode('utf-8')))
                    file.write(bytearray(('#KODIPROP:inputstream.ffmpegdirect.is_realtime_stream=true\n').encode('utf-8')))
                    file.write(bytearray(('#KODIPROP:mimetype=video/mp2t\n').encode('utf-8')))
                file.write(bytearray((line + '\n').encode('utf-8')))
            file.close()
            xbmcgui.Dialog().notification('Rebit.tv', addon.getLocalizedString(300314), xbmcgui.NOTIFICATION_INFO, 5000)    
    except Exception:
        file.close()
        xbmcgui.Dialog().notification('Rebit.tv', addon.getLocalizedString(300313), xbmcgui.NOTIFICATION_ERROR, 5000)

def generate_epg(output_file = ''):
    addon = xbmcaddon.Addon()
    channels = Channels()
    channels_list = channels.get_channels_list('channel_number', visible_filter = False)
    channels_list_by_id = channels.get_channels_list('id', visible_filter = False)

    if len(channels_list) > 0:
        if save_file_test() == 0:
            xbmcgui.Dialog().notification('Rebit.tv', addon.getLocalizedString(300315), xbmcgui.NOTIFICATION_ERROR, 5000)
            return
        output_dir = addon.getSetting('output_dir') 
        try:
            if len(output_file) > 0:
                file = xbmcvfs.File(output_file, 'w')
            else:
                file = xbmcvfs.File(output_dir + 'rebit_epg.xml', 'w')
            if file == None:
                xbmcgui.Dialog().notification('Rebit.tv', addon.getLocalizedString(300315), xbmcgui.NOTIFICATION_ERROR, 5000)
            else:
                file.write(bytearray(('<?xml version="1.0" encoding="UTF-8"?>\n').encode('utf-8')))
                file.write(bytearray(('<tv generator-info-name="EPG grabber">\n').encode('utf-8')))
                content = ''
                for number in sorted(channels_list.keys()):
                    logo = channels_list[number]['logo']
                    if logo is None:
                        logo = ''
                    channel = channels_list[number]['name']
                    content = content + '    <channel id="' + channel.replace('&','&amp;').replace('<','&lt;').replace('>','&gt;') + '">\n'
                    content = content + '            <display-name lang="cs">' + channel.replace('&','&amp;').replace('<','&lt;').replace('>','&gt;') + '</display-name>\n'
                    content = content + '            <icon src="' + logo + '" />\n'
                    content = content + '    </channel>\n'
                file.write(bytearray((content).encode('utf-8')))
                today_date = datetime.today() 
                today_start_ts = int(time.mktime(datetime(today_date.year, today_date.month, today_date.day) .timetuple()))
                today_end_ts = today_start_ts + 60*60*24 - 1
                for number in sorted(channels_list.keys()):
                    cnt = 0
                    content = ''
                    epg =  get_channel_epg(id = channels_list[number]['id'], from_ts = today_start_ts - 60*60*24*7, to_ts = today_end_ts + 60*60*24*7)
                    for ts in sorted(epg.keys()):
                        epg_item = epg[ts]
                        starttime = datetime.fromtimestamp(epg_item['startts']).strftime('%Y%m%d%H%M%S')
                        endtime = datetime.fromtimestamp(epg_item['endts']).strftime('%Y%m%d%H%M%S')
                        content = content + '    <programme start="' + starttime + ' +0' + str(tz_offset) + '00" stop="' + endtime + ' +0' + str(tz_offset) + '00" channel="' + channels_list_by_id[epg_item['channel_id']]['name'] + '">\n'
                        content = content + '       <title lang="cs">' + epg_item['title'].replace('&','&amp;').replace('<','&lt;').replace('>','&gt;') + '</title>\n'
                        if epg_item['description'] != None and len(epg_item['description']) > 0:
                            content = content + '       <desc lang="cs">' + epg_item['description'].replace('&','&amp;').replace('<','&lt;').replace('<','&gt;') + '</desc>\n'
                        content = content + '    </programme>\n'
                        cnt = cnt + 1
                        if cnt > 20:
                            file.write(bytearray((content).encode('utf-8')))
                            content = ''
                            cnt = 0
                    file.write(bytearray((content).encode('utf-8')))                          
                file.write(bytearray(('</tv>\n').encode('utf-8')))
                file.close()
                xbmcgui.Dialog().notification('Rebit.tv', addon.getLocalizedString(300316), xbmcgui.NOTIFICATION_INFO, 5000)    
        except Exception:
            file.close()
            xbmcgui.Dialog().notification('Rebit.tv', addon.getLocalizedString(300315), xbmcgui.NOTIFICATION_ERROR, 5000)
            sys.exit()
    else:
        xbmcgui.Dialog().notification('Rebit.tv', addon.getLocalizedString(300317), xbmcgui.NOTIFICATION_ERROR, 5000)
        sys.exit()
