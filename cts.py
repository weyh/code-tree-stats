# -*- coding: utf-8 -*-
import os
import stat
import argparse
import sys
import threading
import time
from collections import OrderedDict
from itertools import takewhile, repeat, chain
from typing import List

VERSION = "0.9.1"
run_thread = True


class FileData:
    def __init__(self, ext, line_count, file_count):
        self.ext = ext
        self.line_count = line_count
        self.file_count = file_count


class Color:
    reset = u"\u001b[0m"
    black = u"\u001b[30m"
    bright_black = u"\u001b[30;1m"
    red = u"\u001b[31m"
    bright_red = u"\u001b[31;1m"
    green = u"\u001b[32m"
    bright_green = u"\u001b[32;1m"
    yellow = u"\u001b[33m"
    bright_yellow = u"\u001b[33;1m"
    blue = u"\u001b[34m"
    bright_blue = u"\u001b[34;1m"
    magenta = u"\u001b[35m"
    bright_magenta = u"\u001b[35;1m"
    cyan = u"\u001b[36m"
    bright_cyan = u"\u001b[36;1m"
    white = u"\u001b[37m"
    bright_white = u"\u001b[37;1m"


class Table:
    def __init__(self, header: list, datas: List[list]):
        self.__header = header
        self.__datas = datas
        self.__longest_in_column = [0] * len(header)

        for i, col in enumerate(header):
            if len(col) > self.__longest_in_column[i]:
                self.__longest_in_column[i] = len(col)

        for row in datas:
            for i, col in enumerate(row):
                if len(col) > self.__longest_in_column[i]:
                    self.__longest_in_column[i] = len(col)

        return

    def show(self, show_header: bool = True) -> str:
        _table = ""

        if show_header:
            for i, col in enumerate(self.__header):
                _table += '| ' + col + ' ' * (self.__longest_in_column[i] - len(col)) + ' '
            _table += "|\n"

            for col in self.__longest_in_column:
                _table += '|-' + '-' * col + '-'
            _table += "|\n"

        for row in self.__datas:
            for i, col in enumerate(row):
                _table += '| ' + col + ' ' * (self.__longest_in_column[i] - len(col)) + ' '
            _table += "|\n"

        return _table


def print_color(text: str, color="", end="\n"):
    print(color + text + Color.reset, end=end)


def is_binary(file_path: str) -> bool:
    return b'\x00' in open(file_path, 'rb').read()


def is_folder_hidden(folder_path: str) -> bool:
    return "\\." in folder_path or "/." in folder_path


def process_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(usage="%(prog)s [options]")
    parser.add_argument("-V", "--version", action='version', version=f"%(prog)s v{VERSION}")
    parser.add_argument("-c", "--cutoff", metavar="N", default=-1, type=int,
                        help="number of elements to show", required=False)
    parser.add_argument("-B", "--show_binary", default=False, action="store_true",
                        help="show binary files in the list", required=False)
    parser.add_argument("-N", "--hide_negligible", default=False, action="store_true",
                        help=f"hides files with negligible amount of lines (<00.01%%)", required=False)
    parser.add_argument("-A", "--hide_animation", default=False, action="store_true",
                        help=f"hides 'Loading...' text", required=False)

    return parser.parse_args()


def count_lines(file_path: str) -> int:
    f = open(file_path, 'rb')
    bufgen = takewhile(lambda x: x, (f.raw.read(1024*1024)
                                     for _ in repeat(None)))
    return sum(buf.count(b'\n') for buf in bufgen)


def loading_text_animation():
    loading_counter = 0

    while run_thread:
        if(loading_counter > 3):
            loading_counter = 0

        if(loading_counter == 0):
            print("Loading   ", end="\r")
        elif(loading_counter == 1):
            print("Loading.  ", end="\r")
        elif(loading_counter == 2):
            print("Loading.. ", end="\r")
        else:
            print("Loading...", end="\r")

        loading_counter += 1
        time.sleep(0.2)


def loading_bar(count: int, all: int, bar_lenght: int = 22) -> str:
    _bar = ' ' * bar_lenght

    _bar_count = round(len(_bar) * (count / all))
    return '█' * _bar_count + _bar[_bar_count:]


def loading_animation():
    threading.Thread(target=loading_text_animation).start()


def _print_table(file_datas: List[FileData], lines_sum: int, cutoff: int, hide_negligible: bool):
    datas = list()

    percentage_max = 0
    for i, file_data in enumerate(file_datas):
        if i >= cutoff and cutoff != -1:
            break

        _percentage = round(file_data.line_count / lines_sum, 4) * 100
        if _percentage == 100:
            percentage = f"   {(round(file_data.line_count / lines_sum, 4) * 100):03.0f}%"
        else:
            percentage = f" {(round(file_data.line_count / lines_sum, 4) * 100):05.2f}%"

        if _percentage < 0.01 and hide_negligible:
            break

        if i == 0:
            percentage_max = _percentage

        _color = ""
        if _percentage / percentage_max > 0.9:
            _color = Color.bright_red
        elif _percentage / percentage_max > 0.75:
            _color = Color.bright_yellow
        elif _percentage / percentage_max > 0.5:
            _color = Color.bright_blue
        elif _percentage / percentage_max > 0.25:
            _color = Color.bright_magenta

        datas.append([f"{_color}{file_data.ext}{Color.reset}"])  # TODO: fix len() for Color

        # print(_color + file_data.ext + "  " + ' ' * (longest_ext - len(file_data.ext)) + Color.reset +
        #      " | " + _color + loading_bar(file_data.line_count, lines_sum) +
        #      percentage + Color.reset +
        #      f" | {_color}{file_data.file_count}{Color.reset}")

    my_table = Table(["File types", "Lines / all lines", "File count"], datas)


def print_table(file_datas: list, longest_ext: int, lines_sum: int, cutoff: int, hide_negligible: bool):
    print(f"File types {' ' * (longest_ext - 10)}  | Lines / all lines             | File count")
    print(f"{'-' * (longest_ext + 3) }|-------------------------------|-----------")

    percentage_max = 0
    for i, file_data in enumerate(file_datas):
        if i >= cutoff and cutoff != -1:
            break

        _percentage = round(file_data.line_count / lines_sum, 4) * 100
        if _percentage == 100:
            percentage = f"   {(round(file_data.line_count / lines_sum, 4) * 100):03.0f}%"
        else:
            percentage = f" {(round(file_data.line_count / lines_sum, 4) * 100):05.2f}%"

        if _percentage < 0.01 and hide_negligible:
            break

        if i == 0:
            percentage_max = _percentage

        _color = ""
        if _percentage / percentage_max > 0.9:
            _color = Color.bright_red
        elif _percentage / percentage_max > 0.75:
            _color = Color.bright_yellow
        elif _percentage / percentage_max > 0.5:
            _color = Color.bright_blue
        elif _percentage / percentage_max > 0.25:
            _color = Color.bright_magenta

        print(_color + file_data.ext + "  " + ' ' * (longest_ext - len(file_data.ext)) + Color.reset +
              " | " + _color + loading_bar(file_data.line_count, lines_sum) +
              percentage + Color.reset +
              f" | {_color}{file_data.file_count}{Color.reset}")


def main():
    os.system('')

    global run_thread
    path = os.getcwd()
    file_datas_raw = list()
    file_datas = list()
    files_sum = 0
    lines_sum = 0

    longest_ext = 0

    args = process_args()
    if not args.hide_animation:
        loading_animation()

    try:
        for r, d, files in os.walk(path):
            for file in files:
                if ((not is_binary(f"{r}/{file}") or args.show_binary) and len(os.path.splitext(file)[1]) > 1 and not is_folder_hidden(r)):
                    files_sum += 1
                    lc = count_lines(f"{r}/{file}")
                    lines_sum += lc

                    file_datas_raw.append(
                        FileData(os.path.splitext(file)[1].lower(), lc, 0))

        for file_data_raw in file_datas_raw:
            if any(x.ext == file_data_raw.ext for x in file_datas):
                fd = next((x for x in file_datas if x.ext ==
                           file_data_raw.ext), None)

                if len(fd.ext) > longest_ext:
                    longest_ext = len(fd.ext)

                fd.line_count += file_data_raw.line_count
                fd.file_count += 1
            else:
                file_datas.append(
                    FileData(file_data_raw.ext, file_data_raw.line_count, 1))

        file_datas.sort(key=lambda x: x.line_count, reverse=True)
    finally:
        run_thread = False

    if len("File types") > longest_ext:
        longest_ext = len("File types")

    print_table(file_datas, longest_ext + 2, lines_sum,
                args.cutoff, args.hide_negligible)

    print_color(f"\nRoot: {Color.bright_green}{path}")
    print_color(f"Sum of files: {Color.bright_green}{files_sum}")
    print_color(f"Sum of lines: {Color.bright_green}{lines_sum}")


if __name__ == "__main__":
    main()
