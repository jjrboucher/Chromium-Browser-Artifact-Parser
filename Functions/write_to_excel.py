import os.path
import pandas as pd

def write_excel(dataframe, worksheet_name, excel_file):
    """
    Write the dataframe to an Excel file
    :param dataframe: dataframe to write to Excel
    :param worksheet_name: name of the worksheet
    :param excel_file: output file (includes path)
    :return: nil
    """

    white = f'\033[00m'
    green = f'\033[92m'

    if os.path.isfile(excel_file):  # if the Excel file already exists
        # Append to existing Excel file
        with pd.ExcelWriter(excel_file, engine='openpyxl', mode='a') as writer:
            dataframe.to_excel(writer, sheet_name=worksheet_name,  index=False)
    else:
        # Create a new Excel file
        with pd.ExcelWriter(excel_file, engine='openpyxl', mode='w') as writer:
            dataframe.to_excel(writer, sheet_name=worksheet_name, index=False)

    print(f'Query results for worksheet {green}{worksheet_name}{white} saved to Excel file.')