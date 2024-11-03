import json
import pandas as pd
import tkinter as tk
from tkinter import filedialog
from datetime import datetime, timedelta
from Functions.write_to_excel import write_excel

def convert_webkit_timestamp(webkit_timestamp):
    # WebKit timestamp is in microseconds since January 1, 1601
    base_date = datetime(1601, 1, 1)
    # Convert WebKit time (microseconds) to seconds
    timestamp_in_seconds = webkit_timestamp / 1_000_000
    # Add to base date
    human_readable_date = base_date + timedelta(seconds=timestamp_in_seconds)
    return human_readable_date

def get_chromium_bookmarks(bookmark_path):
    rows = []
    if "Bookmarks.bak" in bookmark_path:
        worksheet = "Bookmarks.bak"
    else:
        worksheet = "Bookmarks"

    # Open and load the JSON file
    with open(bookmark_path, 'r', encoding='utf-8') as file:
        bookmarks = json.load(file)

    # Extract bookmarks
    def parse_bookmark_folder(folder, fpath, level=0):
        items = folder.get("children", [])
        for item in items:
            if item.get("type") == "folder":
                date_last_used = convert_webkit_timestamp(int(item.get('date_last_used'))) \
                    if int(item.get('date_last_used')) > 0 else ""
                rows.append([worksheet,
                             'folder',
                             fpath,
                             int(item.get('id')),
                             item.get('name'),
                             item.get('date_added'),
                             convert_webkit_timestamp(int(item.get('date_added'))),
                             item.get('date_last_used'),
                             date_last_used,
                             item.get('date_modified'),
                             convert_webkit_timestamp(int(item.get('date_modified'))),
                             ''
                    ])

                parse_bookmark_folder(item, fpath + "/" + item.get('name'),  level + 1)
            elif item.get("type") == "url":
                date_last_used = convert_webkit_timestamp(int(item.get('date_last_used'))) \
                    if int(item.get('date_last_used')) > 0 else ""
                rows.append([worksheet,
                             'url',
                             fpath,
                             int(item.get('id')),
                             item.get('name'),
                             item.get('date_added'),
                             convert_webkit_timestamp(int(item.get('date_added'))),
                             item.get('date_last_used'),
                             date_last_used,
                             '',
                             '',
                             item.get('url')
                    ])

    # Parse root-level bookmarks
    roots = bookmarks.get("roots", {})

    for root_key, root_folder in roots.items():
        parse_bookmark_folder(root_folder, root_key, 0)

    bookmarks = pd.DataFrame(rows)
    bookmarks.columns = ['Source','Type', 'Folder Path', 'ID', 'Name', 'Date added', 'Converted Date added (UTC)',
                         'Date last used', 'Converted Date last used (UTC)', 'Date Modified (folders only)',
                         'Converted Date Modified (UTC)','URL']
    bookmarks.sort_values(['Folder Path','Type'], ascending=[True, True], inplace=True)
    return bookmarks, worksheet

if __name__ == '__main__':
    red = f'\033[91m'
    white = f'\033[00m'
    green = f'\033[92m'

    # Get the path of the browser profile folder
    root = tk.Tk()
    root.withdraw()  # Hide the main window

    profile_path = filedialog.askdirectory(title="Chrome user profile folder to parse", initialdir=".")

    # Define the path to save the Excel file
    excel_path = filedialog.asksaveasfilename(title="Select a new XLSX file for output (or overwrite existing)",
                                              initialdir=profile_path, filetypes=[("Excel Files", "*.xlsx")],
                                              defaultextension="*.xlsx", confirmoverwrite=True)

    # *** Bookmarks ***
    bookmarks_df, ws = get_chromium_bookmarks(f'{profile_path}/Bookmarks')
    # *** Bookmarks_backup ***
    bookmarks_backup_df, ws_bak = get_chromium_bookmarks(f'{profile_path}/Bookmarks.bak')
    # append bookmarks_backup df to bookmarks df
    all_bookmarks = pd.concat([bookmarks_df, bookmarks_backup_df], ignore_index=True)
    # write all to "Bookmarks" worksheet
    write_excel(all_bookmarks, ws, excel_path)

    print(f'\nAll queries completed. {green}Excel file saved to {excel_path}{white}')
