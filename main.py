if __name__ == '__main__':
    import sqlite3
    import pandas as pd
    from history import history, history_gaps
    from downloads import downloads
    from autofill import autofill

    # Define the path to save the Excel file
    excel_path = 'F:/2023/2023-0492/Edge/edge_browser.xlsx'

    # ***Query History***
    input_file = 'F:/2023/2023-0492/Edge/History'
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
    input_file = 'F:/2023/2023-0492/Edge/Web Data'
    query, worksheet_name = autofill()

    conn = sqlite3.connect(input_file)

    # Execute the query and fetch the results into a pandas DataFrame

    df_autofill = pd.read_sql_query(query, conn)

    # Close the database connection
    conn.close()

    with pd.ExcelWriter(excel_path, mode='a') as writer:
        df_autofill.to_excel(writer, sheet_name=worksheet_name, index=False)

    print(f"Query results for {worksheet_name} saved to {excel_path}")
