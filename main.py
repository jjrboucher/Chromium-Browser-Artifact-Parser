if __name__ == '__main__':
    import sqlite3
    import pandas as pd
    import tkinter as tk
    from tkinter import filedialog
    from history import history, history_gaps
    from downloads import downloads
    from autofill import autofill

    # Get the path of the browser profile folder
    root = tk.Tk()
    root.withdraw()  # Hide the main window

    profile_path = filedialog.askdirectory(title="Chrome user profile folder to parse", initialdir=".")

    # Define the path to save the Excel file
    excel_path = filedialog.asksaveasfilename(title="Select a new XLSX file for output (or overwrite existing)",
                                              initialdir=profile_path, filetypes=[("Excel Files", "*.xlsx")],
                                              defaultextension="*.xlsx", confirmoverwrite=True)

    # ***Query History***
    input_file = f'{profile_path}/History'
    query, worksheet_name = history()

    conn = sqlite3.connect(input_file)

    # Execute the query and fetch the results into a pandas DataFrame

    df_history = pd.read_sql_query(query, conn)

    # Close the database connection
    conn.close()

    df_history.to_excel(excel_path, sheet_name=worksheet_name, index=False)

    print(f"Query results for {worksheet_name} saved to {excel_path}")

    # ***Query History Gaps***
    query, worksheet_name = history_gaps()

    conn = sqlite3.connect(input_file)

    # Execute the query and fetch the results into a pandas DataFrame

    df_history_gaps = pd.read_sql_query(query, conn)

    # Close the database connection
    conn.close()

    with pd.ExcelWriter(excel_path, mode='a') as writer:
        df_history_gaps.to_excel(writer, sheet_name=worksheet_name, index=False)

    print(f"Query results for {worksheet_name} saved to {excel_path}")

    # ***Query Downloads***
    query, worksheet_name = downloads()

    conn = sqlite3.connect(input_file)

    # Execute the query and fetch the results into a pandas DataFrame

    df_downloads = pd.read_sql_query(query, conn)

    # Close the database connection
    conn.close()

    with pd.ExcelWriter(excel_path, mode='a') as writer:
        df_downloads.to_excel(writer, sheet_name=worksheet_name, index=False)

    print(f"Query results for {worksheet_name} saved to {excel_path}")

    # ***Query autofill***
    input_file = f'{profile_path}/Web Data'
    query, worksheet_name = autofill()

    conn = sqlite3.connect(input_file)

    # Execute the query and fetch the results into a pandas DataFrame

    df_autofill = pd.read_sql_query(query, conn)

    # Close the database connection
    conn.close()

    with pd.ExcelWriter(excel_path, mode='a') as writer:
        df_autofill.to_excel(writer, sheet_name=worksheet_name, index=False)

    print(f"Query results for {worksheet_name} saved to {excel_path}")
