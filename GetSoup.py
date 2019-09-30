import re
import bs4
import requests
from re import sub
import math
from _pydecimal import Decimal
from time import sleep
from GetSoup_Helpers import pricecharting_consoles, has_numbers, convert, get_close_matches_indexes



def incapsession_to_soup(url_string):
    sleep(3)
    headers = {
        "User-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.80 Safari/537.36"}

    url = convert(url_string)
    #print("CONVERT:", url)
    res = requests.get(url, headers=headers)
    soup = bs4.BeautifulSoup(res.text, "html.parser")

    return soup


def url_checkers(query, line):

    if has_numbers(line):
        for s in query.split():
            if s.isdigit():
                 if s in line:
                    url_string = line
                    return url_string
    else:
        url_string = line
        return url_string



'''Simple google search that returns url with the used query.'''
def get_google_url(query, game_system):
    url_string = ""
    headers = {
        "User-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.80 Safari/537.36"}

    query = query.replace(":", "")
    #https: // www.pricecharting.com / search - products?type = videogames & q =
    res = requests.get('https://www.google.com/search?q=' + game_system + query, headers=headers)
    print(res.url)
    soup = bs4.BeautifulSoup(res.text, "html.parser")
    links = soup.select('.r a')
    console = pricecharting_consoles[game_system]
    print(console)

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

        if line.startswith('www.pricecharting.com/game/' + console):
        #if line.startswith('www.pricecharting.com/game/nintendo-switch'):
            url_string = line
            print(query, "GOOGLE:", url_string)
            return url_string

    print("Got Blank URL", url_string, "Timed out or Suggest Switching VPN Location")
    return url_string


def get_pricecharting_url(query, game_system):

    headers = {
        "User-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.80 Safari/537.36"}

    game_sys = pricecharting_consoles[game_system]

    print("QUERY:", query)
    file = open("testfile.txt", "w")
    url = 'https://www.pricecharting.com/search-products?type=videogames&q=' + game_system + ' ' + query
    res = requests.get(url, headers=headers)
    print("PC RES:", res.url)
    soup = bs4.BeautifulSoup(res.text, "html.parser")

    skip_pal = "pal-nintendo-switch"

    if 'Game List' in soup.title.string:
        table = soup.find('table', id='games_table')
        titles = table.find_all('td', class_='title')
        titles_text = []

        for title in titles:


            title = re.sub('[^A-Za-z0-9]+', ' ', str(title.text)).strip()
            if query.title().lower() == title.lower():
                titles_text.append(title)
                break
            titles_text.append(title)

        matches = get_close_matches_indexes(query.title(), titles_text, n=1)

        if not matches:
            return "empty.url"

        selected_title = titles[matches[0]]
        link = [a['href'] for a in selected_title.find_all('a', href=True)][0]

        file.write(query + " " + link)
        #print(query, "PC:", link)
        return link
    else:
        file.write(query + " " + res.url)
        #print(query, "PC:", res.url)
        return res.url

#0 = used, 1 = new
def gamestop_find_prices(game):
    soup = incapsession_to_soup(game.url_string)
    gamestop_conditions = soup.find_all("td", class_="store")

    idx = 0
    for store in gamestop_conditions:
        if "GameStop" in store.text:
            price_class = store.find_next('td', class_="price")
            if not price_class.text.isspace():
                price = store.find_next('span', class_="js-price")
                price = price.text.replace("$", "")

                # 0 Loose, 1 Complete, 2 New
                if idx == 0:
                    if game.next_game_match is True:
                        price = math.ceil(float(price)) - .01
                        game.next_game_price = price
                    elif game.c_flag == 1:
                        price = math.ceil(float(price)) - .01
                        game.sell_price = price
                        return
                    else:
                        x = 1
                        # print("Loose:", price)
                    idx = idx + 1
                elif idx == 1:
                    # print("Complete:", price)
                    idx = idx + 1
                elif idx == 2:
                    if game.c_flag == 0:
                        price = math.ceil(float(price)) - .01
                        game.sell_price = price
                        # ("New:", price)
                        return
                else:
                    break

#0 = used, 1 = new
def pricecharting_find_prices(game):
    soup = incapsession_to_soup(game.url_string)
    pricecharting_conditions = soup.find("table", id="price_data")
    tbody = pricecharting_conditions.find_next("tbody")
    conditions = tbody.find_all("span")

    loose = conditions[0].text.replace("$", "")
    complete = conditions[1].text.replace("$", "")
    new = conditions[2].text.replace("$", "")
    loose = loose.replace(" ", "")
    complete = complete.replace(" ", "")
    new = new.replace(" ", "")

    if game.c_flag == 0:
        #new = math.ceil(float(new)) - .01
        game.sell_price = new

    else:
        #loose = math.ceil(float(loose)) - .01
        game.sell_price = loose

    if game.next_game_match is True:
        #loose = math.ceil(float(loose)) - .01
        game.next_game_price = loose






