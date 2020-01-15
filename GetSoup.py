import re
import bs4
import requests
from re import sub
import math
from _pydecimal import Decimal
from time import sleep
from GetSoup_Helpers import pricecharting_consoles, has_numbers, convert, get_close_matches_indexes

headers = {
    "User-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.80 Safari/537.36"}


def incapsession_to_soup(url_string):
    sleep(3)

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
    try:
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
    except AttributeError:
        print("Pc find prices value error")
        return 0





