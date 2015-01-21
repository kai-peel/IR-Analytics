#!/usr/bin/env python
# -*- coding:utf-8 -*-
'''
Created on 2014-10-16

@author: tianyuqi
'''
import sys
from color_console import *
from yg_utils import *

default_colors = get_text_attr()
base = [str(x) for x in range(10)] + [ chr(x) for x in range(ord('A'),ord('A')+6)]

def dec2bin(string_num):
    num = int(string_num)
    if num == 0:
        return '0'
    mid = []
    while True:
        if num == 0:break
        num,rem = divmod(num, 2)
        mid.append(base[rem])

    return ''.join([str(x) for x in mid[::-1]])

def hex2dec(string_num):
    return str(int(string_num.upper(), 16))

def hex2bin(string_num):
    return dec2bin(hex2dec(string_num.upper()))

def output_code(last_code, current_code):
    current_code_list = current_code.split()
    current_code_list = [hex2bin(code) for code in current_code_list]
    fill_gap(current_code_list)
    if last_code:
        last_code_list = last_code.split()
        last_code_list = [hex2bin(code) for code in last_code_list]
        fill_gap(last_code_list)
        compare_to_eachother(last_code_list, current_code_list)
    else:
        sys.stdout.write('  '.join(current_code_list))

# def fill_gap(last_code_list, current_code_list):
#     for index in range(len(current_code_list)):
#         num = abs(len(current_code_list[index]) - len(last_code_list[index]))
#         if len(current_code_list[index]) > len(last_code_list[index]):
#             last_code_list[index] = num * '0' + last_code_list[index]
#         else :
#             current_code_list[index] = num * '0' + current_code_list[index]
        
def fill_gap(code_list):
    for index in range(len(code_list)):
        code_list[index] = (8 - len(code_list[index]))  * '0' + code_list[index]

def compare_to_eachother(last_code_list, current_code_list):
    last_code = '|'.join(last_code_list)
    current_code = '|'.join(current_code_list)
    for index in range(len(current_code)):
        if current_code[index] == last_code[index]:
            set_text_attr(default_colors)
        else:
            set_text_attr(FOREGROUND_RED | BACKGROUND_GREY | FOREGROUND_INTENSITY | BACKGROUND_INTENSITY)
        if current_code[index] == '|':
            sys.stdout.write('  ')
        else:
            sys.stdout.write(current_code[index])

def main():
    last_data_full_code = None
    while True:
        irreader = Listener()
        irreader.run()
        output_code(last_data_full_code, irreader.data_full_code)
        last_data_full_code = irreader.data_full_code
        print

if __name__ == "__main__":
    main()
