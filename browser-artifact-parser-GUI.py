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
from SQLite.WebData import (
    chrome_autofill,
    chrome_keywords,
    chrome_masked_credit_cards,
    chrome_masked_bank_accounts,
    chrome_addresses
)
import openpyxl
import pandas as pd
import sqlite3
import numpy as np
import io

class ChromeParserGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Chrome Parser")
        self.profile_path = None
        self.output_path = None

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

        try:
            chrome_queries = {
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
                "Cookies": [f'{self.profile_path}/Network/Cookies', chrome_cookies],
                "FavIcons": [f'{self.profile_path}/Favicons', chrome_favicons]
            }

            record_counts = []

            for sqlite_query in chrome_queries.keys():
                self.update_status(f"Processing {sqlite_query}...")
                df, ws = self.get_dataframes(chrome_queries[sqlite_query][0], chrome_queries[sqlite_query][1])
                write_excel(df, ws, self.output_path)
                record_counts.append((ws, len(df)))

            self.update_status("Processing Search Terms...")
            dataframe_searchterms, ws = self.process_search_terms()
            write_excel(dataframe_searchterms, ws, self.output_path)
            record_counts.append((ws, len(dataframe_searchterms)))

            self.update_status("Processing Bookmarks...")
            bookmarks_df, ws = get_chromium_bookmarks(f'{self.profile_path}/Bookmarks')
            bookmarks_backup_df, ws_bak = get_chromium_bookmarks(f'{self.profile_path}/Bookmarks.bak')
            all_bookmarks = pd.concat([bookmarks_df, bookmarks_backup_df], ignore_index=True)
            write_excel(all_bookmarks, ws, self.output_path)
            record_counts.append((ws, len(all_bookmarks)))

            self.update_status("Processing Preferences...")
            preferences = Preferences(f'{self.profile_path}/Preferences')
            preferences_output = io.StringIO()
            print(preferences, file=preferences_output)
            preferences_data = preferences_output.getvalue().splitlines()
            preferences_df = pd.DataFrame(preferences_data, columns=["Preferences Output"])
            write_excel(preferences_df, "Preferences", self.output_path)

            self.update_status("Creating Summary Worksheet...")
            summary_df = pd.DataFrame(record_counts, columns=["Worksheet Name", "Record Count"])
            write_excel(summary_df, "Summary", self.output_path)

            # Load the workbook
            self.update_status("Reordering some of the worksheets...")
            wb = openpyxl.load_workbook(self.output_path)

            # Reorganize some of the worksheets
            wb.move_sheet(wb["Summary"], -(len(wb.sheetnames)-1))
            wb.move_sheet(wb["Preferences"], -(len(wb.sheetnames)-2))
            wb.move_sheet(wb["Bookmarks"], -(len(wb.sheetnames)-7))
            wb.move_sheet(wb["Search Terms"], -(len(wb.sheetnames)-7))

            # Save the workbook
            wb.save(self.output_path)

            self.update_status("All processing completed successfully!")
            self.update_status(f'Output saved to {self.output_path}')


        except Exception as e:
            self.update_status(f"Error: {e}")
            messagebox.showerror("Error", f"An error occurred: {e}")

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
