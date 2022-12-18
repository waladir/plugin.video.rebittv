# -*- coding: utf-8 -*-
import sys
import xbmc
import xbmcaddon
import xbmcgui
import string, random
from urllib.parse import urlencode

plugin_id = 'plugin.video.rebittv'

addon = xbmcaddon.Addon()
day_translation = {'1' : addon.getLocalizedString(300400), '2' : addon.getLocalizedString(300401), '3' : addon.getLocalizedString(300402), '4' : addon.getLocalizedString(300403), '5' : addon.getLocalizedString(300404), '6' : addon.getLocalizedString(300405), '0' : addon.getLocalizedString(300406)}  
day_translation_short = {'1' : addon.getLocalizedString(300407), '2' : addon.getLocalizedString(300408), '3' : addon.getLocalizedString(300409), '4' : addon.getLocalizedString(300410), '5' : addon.getLocalizedString(300411), '6' : addon.getLocalizedString(300412), '0' : addon.getLocalizedString(300413)}
adone = None

_url = sys.argv[0]

def check_settings():
    addon = xbmcaddon.Addon()
    if not addon.getSetting('device_id'):
        addon.setSetting('device_id',''.join(random.choice(string.ascii_lowercase + string.digits) for _ in range(15)))

    if not addon.getSetting('username') or not addon.getSetting('password') or not addon.getSetting('device_name'):
        xbmcgui.Dialog().notification('Rebit.tv', addon.getLocalizedString(300200), xbmcgui.NOTIFICATION_ERROR, 10000)
        return False
    else:
        return True

def get_url(**kwargs):
    return '{0}?{1}'.format(_url, urlencode(kwargs))

# kod od listenera
def getNumbers(txt):
    newstr = ''.join((ch if ch in '0123456789' else ' ') for ch in txt)
    return [int(i) for i in newstr.split()]

def formatnum(num):
    num = str(num)
    return num if len(num) == 2 else '0' + num

def parsedatetime(_short, _long):
    ix = _short.find(' ')
    lnums = getNumbers(_long)
    snums = getNumbers(_short[:ix])
    year = max(lnums)
    day = min(lnums)
    snums.remove(day)
    day = formatnum(day)
    month = formatnum(min(snums))
    day_formated = '%s.%s.%i' % (day, month, year)
    time_formated = parsetime(_short[ix + 1:])
    return '%s %s' % (day_formated, time_formated)

def parsetime(txt):
    merid = xbmc.getRegion('meridiem')
    h, m = getNumbers(txt)
    if merid.__len__() > 2:
        AM, PM = merid.split('/')
        if txt.endswith(AM) and h == 12:
            h = 0
        elif txt.endswith(PM) and h < 12:
            h += 12
    return '%02d:%02d' % (h, m)
