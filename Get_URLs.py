import re
import bs4
import requests
from re import sub
import math
from _pydecimal import Decimal
from time import sleep

from GetSoup_Helpers import pricecharting_consoles, get_close_matches_indexes



headers = {
    "User-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.80 Safari/537.36"}

'''Simple google search that returns url with the used query.'''
def get_google_url(query, game_system):
    url_string = ""

    query = query.replace(":", "")
    #https: // www.pricecharting.com / search - products?type = videogames & q =
    res = requests.get('https://www.google.com/search?q=' + game_system + query, headers=headers)

    soup = bs4.BeautifulSoup(res.text, "html.parser")
    links = soup.select('.r a')
    console = pricecharting_consoles[game_system]


    for href in links:
        link = href.get("href")
        if link is None:
            print("LINK ERROR 1:", link)
            continue
        try:
            link = link[8:]
        except ValueError:
            print("LINK ERROR:", query)
            return

        line, mid, end = link.partition('&sa')

        if line.startswith('www.pricecharting.com/game/' + console) or line.startswith(
                "https://www.pricecharting.com/game/" + console):
            url_string = line
            print("GOOGLE:", url_string)
            return url_string

    print("Got Blank URL", url_string, "Timed out or Suggest Switching VPN Location")
    return url_string


def get_pc_upc_url(game):

    console = pricecharting_consoles[game.console]
    url = 'https://www.google.com/search?q=' + 'pricecharting' + game.upc
    res = requests.get(url, headers=headers)
    soup = bs4.BeautifulSoup(res.text, "html.parser")
    links = []

    for link in soup.select('.r a'):
        links.append(link.get('href'))
    print(links[0])
    if links[0].startswith('www.pricecharting.com/game/' + console) or links[0].startswith(
            "https://www.pricecharting.com/game/" + console):
        return links[0]
    else:
        return "empty.url"



def get_pricecharting_url(query, game_system):

    console = pricecharting_consoles[game_system]
    url = 'https://www.pricecharting.com/search-products?type=videogames&q=' + console + ' ' + query
    print(url)
    res = requests.get(url, headers=headers)

    soup = bs4.BeautifulSoup(res.text, "html.parser")

    if 'Game List' in soup.title.string:
        table = soup.find('table', id='games_table')
        titles = table.find_all('td', class_='title')
        #print(titles)
        titles_text = []

        for title in titles:
            temp = title.find('a')
            link = temp.get("href")
            title = re.sub('[^A-Za-z0-9]+', ' ', str(title.text)).strip()

            if link.startswith('www.pricecharting.com/game/' + console) or link.startswith(
                    "https://www.pricecharting.com/game/" + console):
                print(title, link)
                titles_text.append(title)


        matches = get_close_matches_indexes(query.title(), titles_text, n=1)

        if not matches:
            print("PC EMPTY URL")
            return "empty.url"

        selected_title = titles[matches[0]]
        link = [a['href'] for a in selected_title.find_all('a', href=True)][0]


        print("PRICECHARTING:", link)
        return link
    else:
        if res.url.startswith('www.pricecharting.com/game/' + console) or res.url.startswith(
                "https://www.pricecharting.com/game/" + console):
            print("PC2:", res.url)
            return res.url
        else:
            print("empty.url")
            return "empty.url"
