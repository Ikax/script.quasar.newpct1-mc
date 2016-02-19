# coding: utf-8
__author__ = 'mancuniancol'

import common
from bs4 import BeautifulSoup
from quasar import provider

# this read the settings
settings = common.Settings()
# define the browser
browser = common.Browser()
# create the filters
filters = common.Filtering()


def extract_torrents(data):
    print data
    filters.information()  # print filters settings
    sint = common.ignore_exception(ValueError)(int)
    results = []
    cont = 0
    if data is not None:
        soup = BeautifulSoup(data, 'html5lib')
        links = soup.select("ul.buscar-list li a")
        for link in links:
            if link.h2 is not None:
                name = link.h2.text.strip()  # Name
                url = link["href"]
                pos = url.find('/', len(settings.value["url_address"]))
                url = settings.value["url_address"] + "/descarga-torrent" + url[pos:]
                browser.open(url)
                soup = BeautifulSoup(browser.content)
                links_magnets = soup.select("div#tab1 a.btn-torrent")
                if len(links_magnets) > 0:
                    magnet = links_magnets[0].get("href", "")  # magnet
                    links_size = soup.select("span.imp")
                    if len(links_size) > 1:
                        size = links_size[1].text.replace("Size: ", "")  # size
                    else:
                        size = None
                    seeds = 0  # seeds
                    peers = 0  # peers
                    # info_magnet = common.Magnet(magnet)
                    if filters.verify(name, size):
                        # magnet = common.getlinks(magnet)
                        cont += 1
                        results.append({"name": name,
                                        "uri": magnet,
                                        # "info_hash": info_magnet.hash,
                                        "size": size,
                                        # "seeds": sint(seeds),
                                        # "peers": sint(peers),
                                        "language": settings.value.get("language", "es"),
                                        "provider": settings.name,
                                        "icon": settings.icon,
                                        })  # return the torrent
                        if cont >= int(settings.value.get("max_magnets", 10)):  # limit magnets
                            break
                    else:
                        provider.log.warning(filters.reason)
    provider.log.info('>>>>>>' + str(cont) + ' torrents sent to Quasar<<<<<<<')
    return results


def search(query):
    info = {"query": query,
            "type": "general"}
    return search_general(info)


def search_general(info):
    info["extra"] = settings.value.get("extra", "")  # add the extra information
    query = filters.type_filtering(info, '+')  # check type filter and set-up filters.title
    url_search = "%s/buscar" % settings.value["url_address"]
    provider.log.info(url_search)
    payload = {'q': query,
               }
    browser.open(url_search, payload=payload)
    return extract_torrents(browser.content)


def search_movie(info):
    info["type"] = "movie"
    settings.value["language"] = settings.value.get("language", "es")
    if settings.value["language"] == 'en':  # Title in english
        query = info['title'].encode('utf-8')  # convert from unicode
        if len(info['title']) == len(query):  # it is a english title
            query += ' ' + str(info['year'])  # Title + year
        else:
            query = common.IMDB_title(info['imdb_id'])  # Title + year
    else:  # Title en foreign language
        query = common.translator(info['imdb_id'], settings.value["language"], extra=False)  # Just title
    info["query"] = query
    return search_general(info)


def search_episode(info):
    settings.value["language"] = settings.value.get("language", "es")
    if info['absolute_number'] == 0:
        info["type"] = "show"
        if settings.value["language"] != 'es':
            info["query"] = info['title'].encode('utf-8') + ' s%02de%02d' % (
                info['season'], info['episode'])  # define query
        else:
            info["query"] = info['title'].encode('utf-8') + ' %sx%02d' % (
                info['season'], info['episode'])  # define query

    else:
        info["type"] = "anime"
        info["query"] = info['title'].encode('utf-8') + ' %02d' % info['absolute_number']  # define query anime
    return search_general(info)


# This registers your module for use
provider.register(search, search_movie, search_episode)

del settings
del browser
del filters
