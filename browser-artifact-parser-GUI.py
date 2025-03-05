# Written by Jacques Boucher
# email: jjrboucher@gmail.com
# version date: 2025-Mar-05
#
# Script to extract data from Google Chrome's or MS Edge's SQLite databases
# Outputs to an Excel file.
#
# tested with Chrome 129, Edge 129, Opera 113

# Other possible parsing to add:
# Extensions
# Local Storage - LevelDB files. (under {profile}/Local Storage)
# Top Sites

# ***ERROR CHECKING TO ADD***
# DB locked

import tkinter as tk
from tkinter import filedialog, messagebox
from Classes.Preferences import Preferences
from Functions.write_to_excel import write_excel
from JSON.bookmarks import get_chromium_bookmarks
from SQLite.cookies import chrome_cookies
from SQLite.downloads import chrome_downloads, chrome_downloads_gaps
from SQLite.favicons import chrome_favicons
from SQLite.history import chrome_history, chrome_history_gaps
from SQLite.logindata import chrome_login_data, chrome_login_data_gaps
from SQLite.searchterms import chrome_keyword_historyquery
from SQLite.shortcuts import chrome_shortcuts
from SQLite.topsites import chrome_topsites
from SQLite.WebData import (
    chrome_autofill,
    chrome_keywords,
    chrome_masked_credit_cards,
    chrome_masked_bank_accounts,
    chrome_addresses
)
from SQLite.webasssist import edge_webassist

import openpyxl
import pandas as pd
import sqlite3
import numpy as np
import io

class ChromeParserGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Chromium Browser Parser")
        self.profile_path = None
        self.output_path = None

        # icon
        self.icon = tk.PhotoImage(file="./images/browser_chromium_icon.png")
        self.root.iconphoto(False,self.icon)

        # Labels and Buttons
        tk.Label(root, text="Chrome User Profile Folder:").grid(row=0, column=0, sticky="w", padx=10, pady=5)
        self.profile_entry = tk.Entry(root, width=80)
        self.profile_entry.grid(row=0, column=1, padx=10, pady=5)
        tk.Button(root, text="Browse", command=self.browse_profile, bg="green", width=10).grid(row=0, column=2, padx=10, pady=5)

        tk.Label(root, text="Output Excel File:").grid(row=1, column=0, sticky="w", padx=10, pady=5)
        self.output_entry = tk.Entry(root, width=80)
        self.output_entry.grid(row=1, column=1, padx=10, pady=5)
        tk.Button(root, text="Browse", command=self.browse_output, bg="green", width=10).grid(row=1, column=2, padx=10, pady=5)

        tk.Button(root, text="Run Parser", command=self.run_parser, bg="green", width=20).grid(row=2, column=1, pady=20)

        # Status Window
        tk.Label(root, text="Status:").grid(row=3, column=0, sticky="nw", padx=10, pady=5)
        self.status_text = tk.Text(root, height=20, width=70, state="disabled", bg="black", fg="white")
        self.status_text.grid(row=3, column=1, columnspan=2, padx=20, pady=20)

        tk.Button(root, text="Exit", width=10, command=root.destroy, bg="red").grid(row=2, column=2, padx=10, pady=5)

    def update_status(self, message):
        self.status_text.config(state="normal")
        self.status_text.insert(tk.END, message + "\n")
        self.status_text.see(tk.END)
        self.status_text.config(state="disabled")
        root.update()

    def browse_profile(self):
        self.profile_path = filedialog.askdirectory(title="Select Chrome User Profile Folder")
        self.profile_entry.delete(0, tk.END)
        self.profile_entry.insert(0, self.profile_path)

    def browse_output(self):
        self.output_path = filedialog.asksaveasfilename(
            title="Select Output Excel File", defaultextension=".xlsx", filetypes=[("Excel files", "*.xlsx")]
        )
        self.output_entry.delete(0, tk.END)
        self.output_entry.insert(0, self.output_path)

    def run_parser(self):
        if not self.profile_path or not self.output_path:
            messagebox.showerror("Error", "Please select both profile and output paths.")
            return

        chromium_queries = {
            'History': [f'{self.profile_path}/History', chrome_history],
            "History Gaps": [f'{self.profile_path}/History', chrome_history_gaps],
            "Downloads": [f'{self.profile_path}/History', chrome_downloads],
            "Downloads Gaps": [f'{self.profile_path}/History', chrome_downloads_gaps],
            "Autofill": [f'{self.profile_path}/Web Data', chrome_autofill],
            "Addresses": [f'{self.profile_path}/Web Data', chrome_addresses],
            "Keywords": [f'{self.profile_path}/Web Data', chrome_keywords],
            "Credit Cards": [f'{self.profile_path}/Web Data', chrome_masked_credit_cards],
            "Bank Accounts": [f'{self.profile_path}/Web Data', chrome_masked_bank_accounts],
            "Login Data": [f'{self.profile_path}/Login Data', chrome_login_data],
            "Login Data Gaps": [f'{self.profile_path}/Login Data', chrome_login_data_gaps],
            "Shortcuts": [f'{self.profile_path}/Shortcuts', chrome_shortcuts],
            "Top Sites": [f'{self.profile_path}/Top Sites', chrome_topsites],
            "Cookies": [f'{self.profile_path}/Network/Cookies', chrome_cookies],
            "FavIcons": [f'{self.profile_path}/Favicons', chrome_favicons]
        }

        edge_queries = {
            "Web Assist": [f'{self.profile_path}/WebAssistDatabase', edge_webassist]
        }

        record_counts = []

        for sqlite_query in chromium_queries.keys():  # queries for all Chromium based browsers
            self.update_status(f"Processing {sqlite_query}...")

            try:
                df, ws = self.get_dataframes(chromium_queries[sqlite_query][0], chromium_queries[sqlite_query][1])
                write_excel(df, ws, self.output_path)
                record_counts.append((ws, len(df)))
            except Exception as error:
                self.update_status(f'Failed to process {sqlite_query}...')
                record_counts.append((sqlite_query, 0))
                if "database is locked" in str(error):
                    print(f'Error! {chromium_queries[sqlite_query][0]} is locked')
                    self.update_status(f'Error! {chromium_queries[sqlite_query][0]} is locked')

        if "edge" in self.profile_path.lower():  # MS Edge Browser
            for sqlite_query in edge_queries.keys():
                self.update_status(f"Processing {sqlite_query}...")

                try:
                    df, ws = self.get_dataframes(edge_queries[sqlite_query][0], edge_queries[sqlite_query][1])
                    write_excel(df, ws, self.output_path)
                    record_counts.append((ws, len(df)))
                except Exception as error:
                    self.update_status(f'Failed to process {sqlite_query}...')
                    record_counts.append((sqlite_query, 0))
                    if "database is locked" in str(error):
                        print(f'Error! {edge_queries[sqlite_query][0]} is locked')
                        self.update_status(f'Error! {edge_queries[sqlite_query][0]} is locked')

        self.update_status("Processing Search Terms...")
        try:
            dataframe_searchterms, ws = self.process_search_terms()
            write_excel(dataframe_searchterms, ws, self.output_path)
            record_counts.append((ws, len(dataframe_searchterms)))
        except:
            self.update_status("Failed to process Search Terms...")
            record_counts.append(('Search Terms', 0))

        self.update_status("Processing Bookmarks...")
        ws = 'Bookmarks'  # assigning in case it does not get assigned in try/except
        try:
            bookmarks_df, ws = get_chromium_bookmarks(f'{self.profile_path}/Bookmarks')
        except:
            self.update_status("Failed to process Bookmarks...")
            bookmarks_df = pd.DataFrame()  # empty dataframe
        try:
            bookmarks_backup_df, ws_bak = get_chromium_bookmarks(f'{self.profile_path}/Bookmarks.bak')
        except:
            self.update_status("Failed to process Bookmarks.bak...")
            bookmarks_backup_df = pd.DataFrame()  # empty dataframe

        all_bookmarks = pd.concat([bookmarks_df, bookmarks_backup_df], ignore_index=True)
        write_excel(all_bookmarks, ws, self.output_path)
        record_counts.append((ws, len(all_bookmarks)))

        self.update_status("Processing Preferences...")
        try:
            preferences = Preferences(f'{self.profile_path}/Preferences')
            preferences_output = io.StringIO()
            print(preferences, file=preferences_output)
            preferences_data = preferences_output.getvalue().splitlines()
            preferences_df = pd.DataFrame(preferences_data, columns=["Preferences Output"])
            write_excel(preferences_df, "Preferences", self.output_path)
        except:
            self.update_status("Failed to process Preferences...")

        self.update_status("Creating Summary Worksheet...")
        summary_df = pd.DataFrame(record_counts, columns=["Worksheet Name", "Record Count"])
        write_excel(summary_df, "Summary", self.output_path)

        # Load the workbook
        self.update_status("Reordering some of the worksheets...")
        wb = openpyxl.load_workbook(self.output_path)

        # Reorganize some of the worksheets
        wb.move_sheet(wb["Summary"], -(len(wb.sheetnames)-1))

        if 'Preferences' in wb.sheetnames:
            wb.move_sheet(wb["Preferences"], -(len(wb.sheetnames)-2))

        if 'Bookmarks' in wb.sheetnames:
            wb.move_sheet(wb["Bookmarks"], -(len(wb.sheetnames)-7))

        if 'Search Terms' in wb.sheetnames:
            wb.move_sheet(wb["Search Terms"], -(len(wb.sheetnames)-7))

        # Save the workbook
        wb.save(self.output_path)

        self.update_status("All processing completed.")
        self.update_status(f'Output saved to {self.output_path}')


#        except Exception as e:
#            self.update_status(f"Error: {e}")
#            messagebox.showerror("Error", f"An error occurred: {e}")

    def get_dataframes(self, db_file, function):
        query, worksheet_name = function()
        conn = sqlite3.connect(db_file)
        dataframe = pd.read_sql_query(query, conn)
        conn.close()
        return dataframe, worksheet_name

    def process_search_terms(self):
        worksheet = 'Search Terms'
        input_file = f'{self.profile_path}/History'
        df_history, ws_history = self.get_dataframes(input_file, chrome_keyword_historyquery)

        input_file = f'{self.profile_path}/Web Data'
        df_keywords, ws_keyword = self.get_dataframes(input_file, chrome_keywords)

        searchterms = []
        if len(df_keywords) > 0:
            for row in df_history.itertuples():
                if not np.isnan(row[3]):
                    try:
                        kw = [
                            df_keywords.query(f'id == {row[3]}')['keyword'].values[0],
                            df_keywords.query(f'id == {row[3]}')['date_created'].values[0],
                            df_keywords.query(f'id == {row[3]}')['Decoded date_created (UTC)'].values[0],
                            df_keywords.query(f'id == {row[3]}')['last_modified'].values[0],
                            df_keywords.query(f'id == {row[3]}')['Decoded last_modified (UTC)'].values[0]
                        ]
                    except IndexError:
                        kw = ['', '', '', '', '']
                    searchterms.append([
                        row[1], row[2], row[3], kw[0], row[5], row[6], kw[1], kw[2], kw[3], kw[4], row[7], row[8]
                    ])
        else:
            searchterms = [["", "", "", "", "", "", "", "", "", "", "", ""]]

        df_searchterms = pd.DataFrame(searchterms)
        df_searchterms.columns = [
            'URL id', 'url', 'keyword id', 'keyword', 'search term', 'typed_count', 'date_created',
            'Decoded date_created (UTC)', 'last_modified', 'Decoded last_modified (UTC)',
            'last_visit_time (UTC)', 'Decoded last_visit_time (UTC)'
        ]
        return df_searchterms, worksheet

if __name__ == '__main__':
    root = tk.Tk()
    app = ChromeParserGUI(root)
    root.mainloop()
