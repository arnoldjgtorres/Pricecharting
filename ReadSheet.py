import os
import time
import re
from collections import defaultdict
from GetSoup import  pricecharting_find_prices, gamestop_find_prices, get_pricecharting_url, get_google_url
from ReadSheet_Helpers import divide_sheet, find_last_cell, calculate_buyback
from ConvertXLS import open_xls_as_xlsx
import threading

max_threads = 1
data_dict = defaultdict(list)
read_count = 0
skip_count = 0
skip_flag = 0
skipped_games = []
sheet_lock = threading.Lock()

class Game:
    row = None
    c_flag = None
    item_number = None
    game_title = None
    url_string = None
    sell_price = None
    buyback_url_string = None
    buyback_price = None
    retailer = None
    console = None
    previous_sell_price = None
    previous_buyback_price = None

    next_game_match = None
    next_game_item_number = None
    next_game_title = None
    next_game_c_flag = None
    next_game_price = None

    def __init__(self, row, sheet):
        self.row = row
        self.item_number, self.c_flag, self.game_title, self.next_game_item_number, \
            self.next_game_title, self.next_game_c_flag, self.next_game_match,\
            self.previous_buyback_price, self.previous_sell_price\
            = read_game(row, sheet)



'''
Will read excel sheet for game titles and new/used condition.
0 = new    1 = used                                          
'''
def read_game(r, sheet):
    sheet_lock.acquire()
    item_number = sheet.cell(row=r, column=1).value

    if item_number.find("*") == -1:
        c_flag = 0
        g_title = sheet.cell(row=r, column=9).value
    else:
        c_flag = 1
        g_title = sheet.cell(row=r, column=9).value

    next_item_number = sheet.cell(row=r + 1, column=1).value
    temp_next_item_number = ""
    if next_item_number.find("*") == -1:
        next_game_c_flag = 0
        next_game_title = sheet.cell(row=r, column=9).value
    else:
        next_game_c_flag = 1
        temp_next_item_number = next_item_number.replace("*", "")
        next_game_title = sheet.cell(row=r, column=9).value

    previous_sell_price = sheet.cell()
    previous_buyback_price = sheet.cell(row=r, column=5)

    if item_number == temp_next_item_number:
        #print("MATCH:", item_number, " ", next_item_number)
        next_game_match = True
        global skip_flag
        skip_flag = 1
    else:
        next_game_match = False


    sheet_lock.release()
    return item_number, c_flag, g_title, next_item_number, next_game_title, next_game_c_flag, \
           next_game_match, previous_buyback_price, previous_sell_price




def pc_collect_to_sheet(game, sheet, retailer):

    if retailer == 'Gamestop':
        gamestop_find_prices(game)
    elif retailer == 'Pricecharting':
        pricecharting_find_prices(game)

    sheet_lock.acquire()



    '''if next game match is true, then next game is a 'used' game.'''
    if game.next_game_match is True:
        ''' 
        if game.sell_price is none then no price was retrieved and use old price. mostly applies
        to 'new' games that no longer are sold as new at gs.
        '''
        if game.sell_price is None:
            game.sell_price = sheet.cell(row=game.row, column=4).value
        if game.next_game_price is None:
            game.next_game_price = sheet.cell(row=game.row + 1, column=4).value

        game.buyback_price = calculate_buyback(game)
        credit_value = game.buyback_price

        item_list = [game.row + 1, game.next_game_price, credit_value, game.url_string, "Null"]
        data_dict[sheet.cell(row=game.row+1, column=1).value] = item_list

        item_list = [game.row, game.sell_price, credit_value, game.url_string, "Null"]
        data_dict[sheet.cell(row=game.row, column=1).value] = item_list

    else:
        '''
        else we're only looking at one game, and it will either be new or used. most likely a new game
        with a 'used' item not being made in the pos. or a special edition.
        '''
        game.buyback_price = calculate_buyback(game)
        credit_value = game.buyback_price
        item_list = [game.row, game.sell_price, credit_value, game.url_string, "Null"]
        data_dict[sheet.cell(row=game.row, column=1).value] = item_list


    sheet_lock.release()

    global read_count
    read_count = read_count + 1
    #print("Count:", read_count)


def write_to_sheet(sheet):
    for key, value in data_dict.items():
        r = value[0]
        sheet.cell(row=r, column=6).value = value[1]
        sheet.cell(row=r, column=7).value = value[2]
        sheet.cell(row=r, column=10).value = value[3]
        sheet.cell(row=r, column=11).value = value[4]



def done_and_save(sheet, wb, to_file):
    write_to_sheet(sheet)
    desktop = os.path.join(os.path.join(os.environ['USERPROFILE']), 'Desktop')
    save_path = desktop + '\\' + to_file + '.xlsx'
    wb.save(save_path)


def check_deluxes(query):
    deluxe_list = ["D.E", "DE", "D.E.", "L.E", "LE", "L.E.", "DELUXE", "DELUX"]

    for words in deluxe_list:
        for query_word in query.split(): 
            if query_word == words:
                return True
    return False

def title_acronyms(query):
    acronyms = {"PKMN": "POKEMON",
                "SP": "SOUTH PARK",
                "RE": "RESIDENT EVIL"
                }
    for key in acronyms:
        if key in query:
            query = query.replace(key, acronyms[key])
            return query
    return query


#make calls to pricecharting, 2 if need to truncate one word. pricecharting.com url
def make_first_2_pc_calls(game, query, game_system):
    game.url_string = get_pricecharting_url(query, game_system)
    if game.url_string == "empty.url":
        cut_last_word_title = game.game_title.rsplit(' ', 1)[0]
        query = str(cut_last_word_title)
        game.url_string = get_pricecharting_url(query, game_system)


def make_n_google_calls(game, query, game_system, retailer):
    index = 1
    '''below will cut off last word in title of game, sometimes wont give results due to truncated word'''
    length = len(game.game_title.split())
    if game.url_string == "empty.url":
        game.url_string = get_google_url(query, game_system)
        while not game.url_string.startswith('www.pricecharting.com') and length > index and length > 2:
                cut_last_word_title = game.game_title.rsplit(' ', index)[0]
                query = str(retailer) + " " + str(cut_last_word_title) + " " + str(game_system)
                #print(query)
                game.url_string = get_google_url(query, game_system)
                #print(game.url_string)
                index = index + 1


'''Loop through all excel sheet rows to enter sell and buyback prices.'''
def begin_read(game_system, sheet, bounds, retailer):
    for row in range(bounds[0], bounds[1]+1):

        global skip_flag
        if skip_flag == 1:
            skip_flag = 0
            continue

        game = Game(row, sheet)
        game.retailer = retailer
        game.console = game_system
        query = str(game.game_title)
        #query = title_acronyms(query)


        '''
        if check_deluxes(query):
            global skip_count
            skip_count = skip_count + 1
            skipped_games.append(game.game_title)
            #print("SKIPPED DELUXE")
            continue
        '''

        make_first_2_pc_calls(game, query, game_system)
        make_n_google_calls(game, query, game_system, retailer)


        '''
        index = 1
        game.url_string = get_pricecharting_url(query, game_system)
        print("FIRST CALL:", game.url_string)
        if game.url_string == "empty.url":
            cut_last_word_title = game.game_title.rsplit(' ', index)[0]
            query = str(cut_last_word_title)
            game.url_string = get_pricecharting_url(query, game_system)
        #below will cut off last word in title of game, sometimes wont give results due to truncated word
        length = len(game.game_title.split())
        if game.url_string == "empty.url":
            game.url_string = get_google_url(query, game_system)
            while not game.url_string.startswith('www.pricecharting.com') and length > index and length > 2:
                cut_last_word_title = game.game_title.rsplit(' ', index)[0]
                query = str(retailer) + " " + str(cut_last_word_title) + " " + str(game_system)
                # print(query)
                game.url_string = get_google_url(query, game_system)
                # print(game.url_string)
                index = index + 1
        '''


        if not (game.url_string.startswith('www.pricecharting.com') or game.url_string.startswith(
                'https://www.pricecharting.com')) or game.url_string is "empty.url" or game.url_string.isspace() or game.url_string == "":
            print("Doesnt Start With GS or PC:", game.url_string)
            global skip_count
            skip_count = skip_count + 1
            skipped_games.append(game.game_title)
            continue

        print(game.url_string)
        pc_collect_to_sheet(game, sheet, retailer)



'''Program start here, called in GUI_Start'''
def program_start(system, open_file, to_file, retailer, start, end):
    st1 = time.time()
    wb_file = open_file.replace('/', '\\')

    wb = open_xls_as_xlsx(wb_file)
    #wb = openpyxl.load_workbook(wb_file)
    sheet = wb.active
    max_row = find_last_cell(sheet)
    bounds = divide_sheet(max_row, max_threads, int(start), end)

    if max_threads is not 1:
        threads = []

        for bound in bounds:
            t = threading.Thread(target=begin_read, args=(system, sheet, bound, retailer))
            threads.append(t)
        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join()

    else:
        for bound in bounds:
            begin_read(system, sheet, bound, retailer)

    done_and_save(sheet, wb, to_file)
    print(skip_count)
    print(skipped_games)
    print("*** %s secs ***" % (time.time() - st1))
