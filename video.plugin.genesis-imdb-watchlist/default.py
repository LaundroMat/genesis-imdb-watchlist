import xbmc, xbmcgui, xbmcplugin, xbmcaddon
import sys
import re
import feedparser
import urllib

# genesis plugin jsonrpc call:
# {
#   "jsonrpc": "2.0",
#   "method": "Addons.ExecuteAddon",
#   "params": {
#     "wait": false,
#     "addonid": "plugin.video.genesis",
#     "params": {
#       "action": "play",
#       "name": "Avatar (2009)",
#       "title": "Avatar",
#       "year": "2009",
#       "imdb": "0499549",
#       "url": "http://www.imdb.com/title/tt0499549/"
#     }
#   },
#   "id": 2}




# TODO: When looking for available links, remove "The" (i.e. 'The Hunger Games' -> 'Hunger Games')

_WATCHLIST_FEED_URL = "http://rss.imdb.com/user/ur0531641/watchlist"

_GENESIS_PLUGIN_URL = "plugin://plugin.video.genesis/"

_ADDON_NAME = 'plugin.video.genesis-imdb-watchlist'
_addon = xbmcaddon.Addon(id=_ADDON_NAME)
_addon_id = int(sys.argv[1])
_addon_url = sys.argv[0]
_addon_path = _addon.getAddonInfo('path').decode(sys.getfilesystemencoding())


def get_watchlist_entries(feed=_WATCHLIST_FEED_URL):
    xbmc.log("Parsing feed %s" % feed)
    d = feedparser.parse(feed)

    # Plugin needs:
    #       "name": "Avatar (2009)",
    #       "title": "Avatar",
    #       "year": "2009",
    #       "imdb": "0499549",
    #       "url": "http://www.imdb.com/title/tt0499549/"

    return_values = []

    for entry in d.entries:
        data = {}
        data.update({'name':  entry.title})
        year = re.search("\(([^)]*)\)", entry.title).groups()[0]
        title = entry.title.strip("("+year+")").strip()
        data.update({'title': title})
        data.update({'year': year})
        url = entry.link
        data.update({'imdb': url.split("/")[len(url.split("/"))-2][2:]})  # Turn "http://www.imdb.com/title/tt0499549/" into "0499549"
        data.update({'url': url})

        return_values.append(data)

    return return_values


def url_quote(lst):
    return_list = []
    for el in lst:
        for key, value in el.items():
            return_list.append({key: urllib.quote_plus(value)})
    return return_list

feed = _addon.getSetting('watchlist_feed_url')

if feed is None or feed == '':
    xbmc.log("No feed URL found in settings.")
    dialog = xbmcgui.Dialog()

    dialog.ok(
        heading="No IMDB watchlist feed set!",
        line1="Please update plugin settings with your public IMDB watchlist feed URL.",
        line2="Press OK to exit."
    )
    sys.exit()

entries = get_watchlist_entries(feed)
# entries = url_quote(entries)

for entry in entries:
    listitem = xbmcgui.ListItem(label=entry['name'])
    listitem.setProperty('IsPlayable', 'true')
    listitem.setInfo(
        type="video",
        infoLabels={
            'Title': entry['name']
        }
    )

    sources_url = _GENESIS_PLUGIN_URL + "?action=play"
    for key, value in entry.items():
        sources_url += "&%s=%s" % (key, value)

    xbmcplugin.addDirectoryItem(
        _addon_id,
        url=sources_url,
        listitem=listitem,
        isFolder=False,
    )

xbmcplugin.addSortMethod(
    _addon_id,
    xbmcplugin.SORT_METHOD_VIDEO_TITLE
)

xbmcplugin.endOfDirectory(_addon_id, updateListing=True)


