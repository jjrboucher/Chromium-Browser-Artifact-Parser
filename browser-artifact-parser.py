# Written by Jacques Boucher
# email: jjrboucher@gmail.com
# version date: 2024-11-02
#
# Script to extract data from Google Chrome's or MS Edge's SQLite databases
# Outputs to an Excel file.
#
# tested with Chrome 129, Edge 129, Opera 113

# Other parsing to add:
# Bookmarks - completed 27 Oct 2024
# Cookies (under {profile}/Network/Cookies)
# Extensions
# Favicons
# Local Storage - LevelDB files. (under {profile}/Local Storage)
# Top Sites
# Web Data (other tables)

# ***ERROR CHECKING TO ADD***
# DB locked
# User hits cancel rather than selecting a folder, or output Excel file already exists.

# ***TO DO***
# parse bookmarks - Completed 2 Nov 2024
# parse extensions
# parse preferences
# parse top sites
# parse Leveldb files
# Create a summary worksheet with counts of each type of artifact extracted, as well as examiner notes,
# and path and hashes of the SQLite files processed.


import numpy as np  # for np.nan
# import os.path
import pandas as pd
import sqlite3
import tkinter as tk
from tkinter import filedialog

# Import the queries from the other Python files to process Google Chrome artifacts
from Functions.write_to_excel import write_excel
from JSON.bookmarks import get_chromium_bookmarks
from SQLite.cookies import chrome_cookies
from SQLite.downloads import chrome_downloads, chrome_downloads_gaps
from SQLite.favicons import chrome_favicons
from SQLite.history import chrome_history, chrome_history_gaps
from SQLite.logindata import chrome_login_data, chrome_login_data_gaps
from SQLite.searchterms import chrome_keyword_historyquery
from SQLite.shortcuts import chrome_shortcuts
from SQLite.WebData import chrome_autofill, chrome_keywords, chrome_masked_credit_cards, chrome_masked_bank_accounts

red = f'\033[91m'
white = f'\033[00m'
green = f'\033[92m'


def get_dataframes(db_file, function):
    """
    Get the dataframes from the SQLite database
    :param db_file: path and filename of the SQLite database file to query
    :param function: name of the function to run
    :return: returns the dataframe with the query results, and the worksheet name
    """
    query, worksheet_name = function()

    conn = sqlite3.connect(db_file)
    dataframe = pd.read_sql_query(query, conn)
    conn.close()
    return dataframe, worksheet_name


def process_search_terms():
    """
    Process the search terms
    Because the search terms are stored in two different tables, we need to join them.
    The only way to accomplish this is to query each table and store the results in a dataframe.
    Then merge the dataframes on the keyword_id, but only if keyword_id is not NaN.
    :return: dataframe with the search terms, and the worksheet name
    """

    worksheet = 'Search Terms'
    # Get the history data frame
    input_file = f'{profile_path}/History'
    df_history, ws_history = get_dataframes(input_file, chrome_keyword_historyquery)

    # Get the keywords data frame
    input_file = f'{profile_path}/Web Data'
    df_keywords, ws_keyword = get_dataframes(input_file, chrome_keywords)
    # print(f'keywords df: {df_keywords}')
    # input("enter to continue")

    searchterms = []  # list to hold search terms
    if len(df_keywords) > 0:  # if there are keywords, proceed
        for row in df_history.itertuples():  # iterate through the history dataframe to get search terms
            if not np.isnan(row[3]):  # if there is a keyword_id, append the search term to the list
                try:  # sometimes, the corresponding keyword index does not exist in the keywords table in Web Data
                    kw = [df_keywords.query(f'id == {row[3]}')['keyword'].values[0],
                          df_keywords.query(f'id == {row[3]}')['date_created'].values[0],
                          df_keywords.query(f'id == {row[3]}')['Decoded date_created (UTC)'].values[0],
                          df_keywords.query(f'id == {row[3]}')['last_modified'].values[0],
                          df_keywords.query(f'id == {row[3]}')['Decoded last_modified (UTC)'].values[0]
                          ]
                except IndexError:
                    kw = ['', '', '', '', '']
                searchterms.append([row[1],
                                    row[2],
                                    row[3],
                                    kw[0],
                                    row[5],
                                    row[6],
                                    kw[1],
                                    kw[2],
                                    kw[3],
                                    kw[4],
                                    row[7],
                                    row[8]])
    else:
        print('no keywords, so adding an empty row instead')
        searchterms = [["", "", "", "", "", "", "", "", "", "", "", "", ""]]  # if no keywords, adds an empty list instead.

    # add to a new dataframe
    df_searchterms = pd.DataFrame(searchterms)

    df_searchterms.columns = ['URL id',
                              'url',
                              'keyword id',
                              'keyword',
                              'search term',
                              'typed_count',
                              'date_created',
                              'Decoded date_created (UTC)',
                              'last_modified',
                              'Decoded last_modified (UTC)',
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

    # Dictionary of queries to run. Keys are descriptions of the queries,
    # values are lists with the path to the SQLite file and the function to run.
    chrome_queries = {
        'History': [f'{profile_path}/History', chrome_history],
        "History Gaps": [f'{profile_path}/History', chrome_history_gaps],
        "Downloads": [f'{profile_path}/History', chrome_downloads],
        "Downloads Gaps": [f'{profile_path}/History', chrome_downloads_gaps],
        "Autofill": [f'{profile_path}/Web Data', chrome_autofill],
        "Keywords": [f'{profile_path}/Web Data', chrome_keywords],
        "Credit Cards": [f'{profile_path}/Web Data', chrome_masked_credit_cards],
        "Bank Accounts": [f'{profile_path}/Web Data', chrome_masked_bank_accounts],
        "Login Data": [f'{profile_path}/Login Data', chrome_login_data],
        "Login Data Gaps": [f'{profile_path}/Login Data', chrome_login_data_gaps],
        "Shortcuts": [f'{profile_path}/Shortcuts', chrome_shortcuts],
        "Cookies": [f'{profile_path}/Network/Cookies', chrome_cookies],
        "FavIcons": [f'{profile_path}/Favicons', chrome_favicons]
    }

    for sqlite_query in chrome_queries.keys():  # iterate through the dictionary of queries
        df, ws = get_dataframes(chrome_queries[sqlite_query][0], chrome_queries[sqlite_query][1])
        write_excel(df, ws, excel_path)

    # ***Query Search Terms***
    dataframe_searchterms, ws = process_search_terms()
    write_excel(dataframe_searchterms, ws, excel_path)

    # *** Bookmarks ***
    bookmarks_df, ws = get_chromium_bookmarks(f'{profile_path}/Bookmarks')
    # *** Bookmarks_backup ***
    bookmarks_backup_df, ws_bak = get_chromium_bookmarks(f'{profile_path}/Bookmarks.bak')
    # append bookmarks_backup df to bookmarks df
    all_bookmarks = pd.concat([bookmarks_df, bookmarks_backup_df], ignore_index=True)
    # write all to "Bookmarks" worksheet
    write_excel(all_bookmarks, ws, excel_path)

    # *** use the compare feature in pandas to report what is different between bookmarks and backups.

    print(f'\nAll queries completed. {green}Excel file saved to {excel_path}{white}')
