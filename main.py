import os.path
import sqlite3
import tkinter as tk
from tkinter import filedialog

import numpy as np  # for np.nan
import pandas as pd

from autofill import chrome_autofill
from downloads import chrome_downloads, chrome_downloads_gaps
from history import chrome_history, chrome_history_gaps
from logindata import chrome_login_data, chrome_login_data_gaps
from searchterms import chrome_historyquery, chrome_keywordsquery
from shortcuts import chrome_shortcuts

red = f'\033[91m'
white = f'\033[00m'
green = f'\033[92m'

def get_dataframes(db_file, function):
    query, worksheet_name = function()

    conn = sqlite3.connect(db_file)
    dataframe = pd.read_sql_query(query, conn)
    conn.close()
    return dataframe, worksheet_name

def write_excel(dataframe, worksheet_name):
    global excel_path

    if os.path.isfile(excel_path): # if the Excel file already exists
        # Append to existing Excel file
        with pd.ExcelWriter(excel_path, mode='a') as writer:
            dataframe.to_excel(writer, sheet_name=worksheet_name, index=False)
    else:
        # Create a new Excel file
        with pd.ExcelWriter(excel_path, mode='w') as writer:
            dataframe.to_excel(writer, sheet_name=worksheet_name, index=False)

    print(f'Query results for worksheet {green}{worksheet_name}{white} saved to Excel file.')

def process_search_terms():
    worksheet = 'Search Terms'
    # Get the history data frame
    input_file = f'{profile_path}/History'
    df_history, ws_history = get_dataframes(input_file, chrome_historyquery)

    # Get the keywords data frame
    input_file = f'{profile_path}/Web Data'
    df_keywords, ws_keyword = get_dataframes(input_file, chrome_keywordsquery)

    searchterms = []  # list to hold search terms
    for row in df_history.itertuples():  # iterate through the history dataframe to get search terms
        if not np.isnan(row[3]):  # if there is a keyword_id, append the search term to the list
            searchterms.append([row[1],
                               row[2],
                               df_keywords.query(f'id == {row[3]}')['keyword'].values[0],
                               row[5],
                               row[6],
                               row[7],
                               row[8]])

    # add to a new dataframe
    df_searchterms = pd.DataFrame(searchterms)

    df_searchterms.columns = ['id',
                              'url',
                              'keyword',
                              'search term',
                              'typed_count',
                              'last_visit_time (UTC)',
                              'Decoded last_visit_time (UTC)']

    return df_searchterms, worksheet

if __name__ == '__main__':


    # Get the path of the browser profile folder
    root = tk.Tk()
    root.withdraw()  # Hide the main window

    profile_path = filedialog.askdirectory(title="Chrome user profile folder to parse", initialdir=".")

    # Define the path to save the Excel file
    excel_path = filedialog.asksaveasfilename(title="Select a new XLSX file for output (or overwrite existing)",
                                              initialdir=profile_path, filetypes=[("Excel Files", "*.xlsx")],
                                              defaultextension="*.xlsx", confirmoverwrite=True)

    chrome_queries = {
        'History': [f'{profile_path}/History', chrome_history],
        "History Gaps": [f'{profile_path}/History', chrome_history_gaps],
        "Downloads": [f'{profile_path}/History', chrome_downloads],
        "Downloads Gaps": [f'{profile_path}/History', chrome_downloads_gaps],
        "Autofill": [f'{profile_path}/Web Data', chrome_autofill],
        "Login Data": [f'{profile_path}/Login Data', chrome_login_data],
        "Login Data Gaps": [f'{profile_path}/Login Data', chrome_login_data_gaps],
        "Shortcuts": [f'{profile_path}/Shortcuts', chrome_shortcuts]
    }

    for sqlite_query in chrome_queries.keys():  # iterate through the dictionary of queries
        df, ws = get_dataframes(chrome_queries[sqlite_query][0], chrome_queries[sqlite_query][1])
        write_excel(df, ws)

    # ***Query Search Terms***
    dataframe_searchterms, ws = process_search_terms()
    write_excel(dataframe_searchterms, ws)

    print(f'\nAll queries completed. {green}Excel file saved to {excel_path}{white}')
