import numpy as np
import pandas as pd
import tkinter as tk
from tkinter.filedialog import askopenfilename
from pandastable import Table
import warnings
import configparser


class MyApp:
    def __init__(self, calorie_changes_path, food_nutrition_file_path):
        self.intermediate_food_nutrition_file_name = None
        self.intermediate_calorie_changes_file_name = None
        self.settings_popup = None
        self.calorie_changes_file_name = calorie_changes_path
        self.food_nutrition_file_name = food_nutrition_file_path
        self.root = tk.Tk()
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)

        self.frm = tk.Frame(self.root)
        self.frm.columnconfigure(0, weight=0)
        self.frm.columnconfigure(1, weight=1)
        self.frm.rowconfigure(0, weight=0)
        self.frm.rowconfigure(1, weight=1)
        self.frm.grid(row=0, column=0, sticky="nsew")
        self.root.title("Calorie table summary")
        self.add_menu()

        self.group_by_option = tk.StringVar(self.frm)
        self.group_by_option.set("item")
        self.my_function()
        selections = ["ingredient", "item", "day", "week", "month", "year", "decade", "century", "eon"]
        label = tk.Label(self.frm, text="aggregation: ")
        label.grid(column=0, row=0, pady=2, padx=2)
        lb = tk.OptionMenu(self.frm, self.group_by_option, *selections, command=self.my_function)
        lb.grid(column=1, row=0, pady=2, padx=2, sticky="W")
        self.root.mainloop()
        self.mtable = None

    def my_function(self, _=None):
        frame2 = tk.Frame(self.frm)
        frame2.grid(column=0, row=1, sticky="NSEW", padx=2, pady=2, columnspan=2)

        self.mtable = Table(frame2, dataframe=self.get_table(), showtoolbar=True, showstatusbar=True, width=1250,
                            height=600)
        self.mtable.grid(column=0, row=0, sticky="NSEW", padx=2, pady=2)
        self.mtable.show()

    def get_table(self):
        calorie_changes = pd.read_csv(self.calorie_changes_file_name)
        food_nutrition = pd.read_csv(self.food_nutrition_file_name)

        merged = calorie_changes.merge(food_nutrition, how="left", on='name')
        merged.fillna(0, inplace=True)
        amounts = pd.to_numeric(merged["amount"].str[:-1])
        multiplier = np.where(merged["amount"].str[-1] == 'g', 100, 1)
        multiplier = np.where(merged["amount"].str[-1] == 'm', 60, multiplier)
        cols = list(food_nutrition.columns)
        cols.remove("name")
        for col in cols:
            merged[col] = merged[col] * amounts / multiplier
        if self.group_by_option.get() == "item":
            pass
        elif self.group_by_option.get() == "day":
            merged.drop(["name", "amount"], axis=1, inplace=True)
            merged = merged.groupby(["date"]).sum()
            merged.reset_index(inplace=True)
        elif self.group_by_option.get() == "week":
            weeks = pd.to_datetime(merged["date"]).dt.isocalendar()[["year", "week"]]
            merged.drop(["date", "name", "amount"], axis=1, inplace=True)
            merged = pd.concat([weeks, merged], axis=1)
            merged = merged.groupby(["year", "week"]).sum()
            merged.reset_index(inplace=True)
        elif self.group_by_option.get() == "month":
            dates = pd.to_datetime(merged["date"])
            years = dates.dt.year
            years.name = "year"
            months = dates.dt.month
            months.name = "month"
            merged.drop(["date", "name", "amount"], axis=1, inplace=True)
            merged = pd.concat([years, months, merged], axis=1)
            merged = merged.groupby(["year", "month"]).sum()
            merged.reset_index(inplace=True)
        elif self.group_by_option.get() == "year":
            dates = pd.to_datetime(merged["date"])
            years = dates.dt.year
            years.name = "year"
            merged.drop(["date", "name", "amount"], axis=1, inplace=True)
            merged = pd.concat([years, merged], axis=1)
            merged = merged.groupby(["year"]).sum()
            merged.reset_index(inplace=True)
        else:
            raise NotImplementedError
        return merged

    def add_menu(self):
        menubar = tk.Menu(self.root)
        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(label="Settings", command=self.show_settings)

        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.quit)
        menubar.add_cascade(label="File", menu=file_menu)

        help_menu = tk.Menu(menubar, tearoff=0)
        help_menu.add_command(label="Help", command=self.show_help)
        help_menu.add_command(label="About", command=self.show_about)
        menubar.add_cascade(label="Help", menu=help_menu)

        self.root.config(menu=menubar)

    def show_help(self):
        popup = tk.Toplevel(self.root)
        tk.Label(popup, text="Choose from the aggregation selection. You can target 2000 kcalories a day")\
            .pack(padx=5, pady=5)
        popup.title("Help")
        tk.Button(popup, text="Ok", command=popup.destroy).pack()

    def show_about(self):
        popup = tk.Toplevel(self.root)
        tk.Label(popup, text="Kristof Kornis, 2024").pack(padx=50, pady=5)
        popup.title("About")
        tk.Button(popup, text="Ok", command=popup.destroy).pack()

    def show_settings(self):
        self.settings_popup = tk.Toplevel(self.root)
        self.settings_popup.grid()
        self.settings_popup.title("Settings")
        self.intermediate_food_nutrition_file_name = self.food_nutrition_file_name
        self.intermediate_calorie_changes_file_name = self.calorie_changes_file_name
        tk.Button(self.settings_popup, text="set food nutrition file", command=self.set_food_nutrition_file_name)\
            .grid(row=0, column=0)
        tk.Label(self.settings_popup, text=self.intermediate_food_nutrition_file_name).grid(row=0, column=1)
        tk.Button(self.settings_popup, text="set calorie changes file", command=self.set_calorie_changes_file_name)\
            .grid(row=1, column=0)
        tk.Label(self.settings_popup, text=self.intermediate_calorie_changes_file_name).grid(row=1, column=1)
        tk.Button(self.settings_popup, text="Ok", command=self.settings_ok).grid(row=2, column=1)
        tk.Button(self.settings_popup, text="Cancel", command=self.settings_cancel).grid(row=2, column=2)
        tk.Button(self.settings_popup, text="Apply", command=self.settings_apply).grid(row=2, column=3)

    def set_food_nutrition_file_name(self):
        self.intermediate_food_nutrition_file_name = askopenfilename()

    def set_calorie_changes_file_name(self):
        self.intermediate_calorie_changes_file_name = askopenfilename()

    def settings_ok(self):
        self.food_nutrition_file_name = self.intermediate_food_nutrition_file_name
        self.calorie_changes_file_name = self.intermediate_calorie_changes_file_name
        self.settings_popup.destroy()

    def settings_cancel(self):
        self.settings_popup.destroy()

    def settings_apply(self):
        self.food_nutrition_file_name = self.intermediate_food_nutrition_file_name
        self.calorie_changes_file_name = self.intermediate_calorie_changes_file_name


def main():
    config = configparser.ConfigParser()

    calorie_changes_path = "calorie_changes.csv"
    food_nutrition_file_path = "food_nutrition.csv"
    if config.read('settings.ini'):
        if "DEFAULT" in config:
            if "calorie_changes_path" in config["DEFAULT"]:
                calorie_changes_path = config["DEFAULT"]["calorie_changes_path"]
            if "food_nutrition_file_path" in config["DEFAULT"]:
                food_nutrition_file_path = config["DEFAULT"]["food_nutrition_file_path"]

    with warnings.catch_warnings() as _:
        warnings.filterwarnings("ignore", r"the convert_dtype parameter is deprecated and will be removed in a future "
                                          r"version.", FutureWarning)
        MyApp(calorie_changes_path, food_nutrition_file_path)


if __name__ == "__main__":
    main()
