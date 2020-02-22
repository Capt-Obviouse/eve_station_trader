from tkinter import Tk
from time import sleep
from decimal import *
from threading import Thread
import pyperclip
from termcolor import colored, cprint
import os
import numpy as np
from terminaltables import SingleTable


r = Tk()

r.withdraw()

rows, columns = os.popen("stty size", "r").read().split()

np.set_printoptions(linewidth=columns)


def comma_value(max_buy):
    return format(max_buy, ",")


class bcolors:

    HEADER = "\033[95m"
    OKBLUE = "\033[94m"
    OKGREEN = "\033[92m"
    WARNING = "\033[93m"
    FAIL = "\033[91m"
    ENDC = "\033[0m"

    def disable(self):
        self.HEADER = ""
        self.OKBLUE = ""
        self.OKGREEN = ""
        self.WARNING = ""
        self.FAIL = ""
        self.ENDC = ""


class Main:
    def __init__(self):
        self.capital = 1000
        self.order_count = 20
        self.volume_multiplier = 5
        self.storage = ""
        self.order_price = 0
        self.margin_skill = 4
        # 0 = Buy | 1 = Sell | 2 = off
        self.mode = 0
        self.competitive_price = 0
        self.margin = 0.10
        self.min_margin = 0.05
        self.__FINISH = False

        self.setup()
        self.run()

    def clear_term(self):
        os.system("cls" if os.name == "nt" else "clear")

    def display_header(self):
        if self.mode == 0:
            hr_mode = "Buy"
        elif self.mode == 1:
            hr_mode = "Sell"
        else:
            hr_mode = "Off"

        hr_margin = "{}%".format(self.margin * 100)

        mode = "Mode: {}".format(hr_mode)
        capital = "Capital: {}".format(self.capital)
        volume = "Volume Multi: {}".format(self.volume_multiplier)
        divider = "=======" * 10
        margin = "Min Margin: {}".format(hr_margin)
        print(
            "{}\n{:<2}  {:<2}  {:<2}  {:<2}\n{}\n".format(
                divider, mode, capital, volume, margin, divider
            )
        )

    def calculate_order_price(self):
        capital = self.capital * 1000000
        margin_capital = (
            capital * Decimal(0.75) ** Decimal(self.margin_skill)
        ) + capital
        order_price = Decimal(margin_capital) / Decimal(self.order_count)
        self.order_price = round(order_price, 2)

    def calculate_profit(self, buy, sell):
        profit = sell - buy
        return round(profit, 2)

    def calculate_needed_qty(self, value):
        qty = self.order_price / value
        return round(qty, 0)

    def calculate_min_daily_volume(self, value):
        return value * self.volume_multiplier

    def convert_daily_volume_thousands(self, value):
        new_value = value / 1000
        if new_value < 0.01:
            return "N/A"

        conversion = "{} K".format(round(new_value, 2))

        return conversion

    def convert_daily_volume_millions(self, value):
        new_value = value / 1000000
        if new_value < 0.01:
            return "N/A"

        conversion = "{} M".format(round(new_value, 2))

        return conversion

    def convert_daily_volume_billions(self, value):
        new_value = value / 1000000000
        if new_value < 0.09:
            return "N/A"

        conversion = "{} B".format(round(new_value, 2))
        return conversion

    def calculate_cost(self, value):
        margin = Decimal(self.min_margin)
        margin += 1
        value_with_margin = value * margin
        return round(value_with_margin, 2)

    def calculate_margin_sell(self, value):
        margin = Decimal(self.margin)
        margin += 1
        value_with_margin = value * margin
        return round(value_with_margin, 2)

    def calculate_max_buy(self, value):
        margin = Decimal(self.margin)
        margin += 1
        value_with_margin = value / margin
        return round(value_with_margin, 2)

    def calculate_max_cost(self, value):
        margin = Decimal(self.min_margin)
        margin += 1
        value_with_margin = value / margin
        return round(value_with_margin, 2)

    def calculate_competitive_price(self, value):
        if self.mode == 0:
            return round(value + Decimal(0.01), 2)
        else:
            return round(value - Decimal(0.01), 2)

    def parse_value(self, value):
        split_value = value.split()
        price_location = 0
        loc = 0
        for location in split_value:
            if location == "ISK":
                price_location = loc - 1
                break
            loc += 1
        price = Decimal(split_value[price_location].replace(",", ""))
        return round(price, 2)

    def get_results(self, data):
        value = self.parse_value(data)
        margin_sell = self.calculate_margin_sell(value)
        cost = self.calculate_cost(value)
        max_margin_buy = self.calculate_max_buy(value)
        max_cost = self.calculate_max_cost(value)
        profit = self.calculate_profit(value, margin_sell)

        needed_qty = self.calculate_needed_qty(value)
        min_daily_volume = self.calculate_min_daily_volume(needed_qty)
        daily_volume_thousands = self.convert_daily_volume_thousands(min_daily_volume)
        daily_volume_millions = self.convert_daily_volume_millions(min_daily_volume)
        daily_volume_billions = self.convert_daily_volume_billions(min_daily_volume)
        competitive_price = self.calculate_competitive_price(value)
        self.competitive_price = competitive_price
        pyperclip.copy(str(competitive_price))

        divider = "=======" * 10
        sub_divider = "_______" * 10
        if self.mode == 0:
            table_data = [
                [
                    "Min Sell",
                    colored(comma_value(margin_sell), "grey", "on_red", attrs=["bold"]),
                ],
                ["Profit Per Unit", comma_value(profit)],
                ["Cost", comma_value(cost)],
                ["Competitive Price", comma_value(competitive_price)],
            ]
            try:
                for item in table_data:
                    print("{:<40}{}\n".format(item[0], item[1]))
            except Exception as e:
                print(e)

            print(
                "{}\n\nQty: {:,.0f}\n\nMin Volume\n{:,.0f}\n{}\n{}\n{}\n".format(
                    sub_divider,
                    needed_qty,
                    min_daily_volume,
                    daily_volume_thousands,
                    daily_volume_millions,
                    daily_volume_billions,
                )
            )
        else:
            try:
                print(
                    "Competitive Price: {}\n\nMax Margin Price: {}\n\nMax Cost {}".format(
                        comma_value(competitive_price),
                        colored(
                            comma_value(max_margin_buy),
                            "grey",
                            "on_red",
                            attrs=["bold", "underline"],
                        ),
                        comma_value(max_cost),
                    )
                )
            except Exception as e:
                print(e)

    def get_clip_data(self):
        while not r.selection_get(selection="CLIPBOARD"):
            sleep(0.1)
        result = r.selection_get(selection="CLIPBOARD")
        return result

    def setup(self):
        use_defaults = input("Use Defaults? enter to continue, n to change")

        if use_defaults != "n":
            return self.calculate_order_price()

        self.capital = Decimal(
            input("Please enter a starting capital in millions\n default: 1000\n ")
            or self.capital
        )
        self.volume_multiplier = Decimal(
            input("Please enter a volume multiplier\n default: 5\n ")
            or self.volume_multiplier
        )

        self.order_count = Decimal(
            input("Please enter a desired order count:\n default: 20\n")
            or self.order_count
        )
        self.margin_skill = Decimal(
            input("Please enter your Margin Trade Skill Level:\n default: 4\n")
            or self.margin_skill
        )

        self.calculate_order_price()

    def user_input(self):
        while True:
            if self.__FINISH:
                break
            users_input = input("Please enter an option\n")

            if users_input == "q" or users_input == "Q":
                print("quitting")
                self.__FINISH = True
            if users_input == "b":
                self.mode = 0
                print("buy mode\n")
            if users_input == "s":
                self.mode = 1
                print("sell mode\n")
            if users_input == "o":
                self.mode = 2
                print("Off")

            if users_input == "capital":
                self.capital = Decimal(
                    input("Please enter new capital in millions\n") or self.capital
                )

            if users_input == "orders":
                self.order_count = Decimal(
                    input("Please enter a desired order count:\n default: 20\n")
                    or self.order_count
                )

            if users_input == "volume":
                self.volume_multiplier = Decimal(
                    input("Please enter a volume multiplier\n default: 5\n ")
                    or self.volume_multiplier
                )
            if users_input == "margin":
                self.margin_skill = Decimal(
                    input("Please enter your Margin Trade Skill Level:\n default: 4\n")
                    or self.margin_skill
                )

            if users_input:
                self.clear_term()
                self.display_header()

            if users_input == "h" or users_input == "help":
                print(
                    """
    Options:
        q, Q
            Quit
        b
            Change mode to BUY
        s
            Change mode to SELL
        o
            Off
        capital
            Change capital amount
        orders
            Change order count
        volume
            Change volume multiplier
        margin
            Change margin skill level
        settings
            List current settings
                """
                )
            if users_input == "settings":
                print(
                    """
    Current Settings
    ----------------
    Captial In Millions:  {}
    Order Count:          {}
    Volume Multiplier:    {}
    Margin Skill Level:   {}
                        """.format(
                        self.capital,
                        self.order_count,
                        self.volume_multiplier,
                        self.margin_skill,
                    )
                )

    def clip_data(self):
        t1 = Thread(target=self.user_input)
        t1.start()
        count = 0
        minute_in_seconds = 60
        idle_minutes = 5
        total_seconds = idle_minutes * minute_in_seconds
        while True:
            if self.__FINISH:
                t1.join()
                self.clear_term()
                quit()
            if self.mode == 2:
                sleep(0.5)
                continue
            if count > total_seconds:
                self.mode = 2
                count = 0
                print("Auto Off")
                continue
            count += 1
            sleep(0.1)
            result = self.get_clip_data()
            if result == self.storage:
                sleep(0.5)
                continue
            if result == str(self.competitive_price):
                sleep(0.5)
                continue
            self.storage = result
            try:
                self.clear_term()
                self.display_header()

                self.get_results(result)
            except Exception as e:
                continue

            count = 0
            print("\nPlease enter an option")

    def run(self):
        self.clip_data()


Main()
