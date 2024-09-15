import os.path
import pandas as pd
import sqlite3
import tkinter as tk
from tkinter import filedialog
from history import history, history_gaps
from downloads import downloads, downloads_gaps
from autofill import autofill, autofill_profile
from logindata import login_data, login_data_gaps
from shortcuts import shortcuts

red = f'\033[91m'
white = f'\033[00m'
green = f'\033[92m'

def query_db(db_file, function):
    global excel_path
    query, worksheet_name = function()

    conn = sqlite3.connect(db_file)

    # Execute the query and fetch the results into a pandas DataFrame
    df = pd.read_sql_query(query, conn)

    # Close the database connection
    conn.close()

    if os.path.isfile(excel_path): # if the Excel file already exists
        # Append to existing Excel file
        with pd.ExcelWriter(excel_path, mode='a') as writer:
            df.to_excel(writer, sheet_name=worksheet_name, index=False)
    else:
        # Create a new Excel file
        with pd.ExcelWriter(excel_path, mode='w') as writer:
            df.to_excel(writer, sheet_name=worksheet_name, index=False)

    print(f'Query results for worksheet {green}{worksheet_name}{white} saved to Excel file {green}{excel_path}{white}')


if __name__ == '__main__':


    # Get the path of the browser profile folder
    root = tk.Tk()
    root.withdraw()  # Hide the main window

    profile_path = filedialog.askdirectory(title="Chrome user profile folder to parse", initialdir=".")

    # Define the path to save the Excel file
    excel_path = filedialog.asksaveasfilename(title="Select a new XLSX file for output (or overwrite existing)",
                                              initialdir=profile_path, filetypes=[("Excel Files", "*.xlsx")],
                                              defaultextension="*.xlsx", confirmoverwrite=True)

    input_file = f'{profile_path}/History'
    # ***Query History***
    query_db(input_file, history)

    # ***Query History Gaps***
    query_db(input_file, history_gaps)

    # ***Query Downloads***
    query_db(input_file, downloads)

    # ***Query Downloads Gaps***
    query_db(input_file, downloads_gaps)

    # ***Query autofill***
    input_file = f'{profile_path}/Web Data'
    query_db(input_file, autofill)

    # ***Query autofill_profile***
    # only works with older versions of Chrome. Commented out for now.
    # query_db(input_file, autofill_profile)

    # ***Query Login Data***
    input_file = f'{profile_path}/Login Data'
    query_db(input_file, login_data)

    # ***Query Login Data Gaps***
    query_db(input_file, login_data_gaps)

    # ***Query Shortcuts***
    input_file = f'{profile_path}/Shortcuts'
    query_db(input_file, shortcuts)