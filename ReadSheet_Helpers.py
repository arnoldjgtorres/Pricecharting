import math
import numpy as np
import os

def split_sheet_into_parts(start, number, n_parts):
    return np.linspace(int(start), int(number), n_parts+1)[1:]


def divide_sheet(max_row, max_threads, start, end):

    if end != "Max Row":
        max_row = end

    my_array = split_sheet_into_parts(start, max_row, max_threads).tolist()

    list_pairs = [(start, math.ceil(my_array[0]))]

    for entry in my_array[:-1]:
        list_pairs.append((math.ceil(entry+1), math.ceil(my_array[my_array.index(entry)+1])))
    print(list_pairs)
    return list_pairs


def find_last_cell(sheet):
    for r in range(1, sheet.max_row+1):
        cell = sheet.cell(row=r, column=1).value
        if len(cell.strip()) == 0:
            return r-1

def find_gecko(file):
    home = os.path.abspath(os.sep)
    for root, dirs, files in os.walk(home):
        if file in files:
            print(os.path.join(root, file))
            return os.path.join(root, file)

def calculate_buyback(game):
    if game.c_flag == "0":
        if game.sell_price == 0:
            return game.previous_buyback_price
        else:
            return float(game.sell_price)/2

    else:
        #TODO CALCULATE USED BUYBACK
        return 5


    return 0
