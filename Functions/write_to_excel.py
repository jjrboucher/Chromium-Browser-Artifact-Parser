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

    # Sanitize control characters that are illegal in XML (and therefore in xlsx).
    # openpyxl raises IllegalCharacterError if any cell contains bytes 0x00-0x08,
    # 0x0B, 0x0C, or 0x0E-0x1F.  These can appear in free-text fields pulled from
    # SQLite (e.g. content_annotations.related_searches, search_terms).
    # This strips them while preserving tabs (0x09), newlines (0x0A), and
    # carriage returns (0x0D) which are valid in XML.
    # Only applied to string (object) columns to avoid disrupting numeric dtypes.
    str_cols = dataframe.select_dtypes(include=['object']).columns
    if len(str_cols) > 0:
        dataframe[str_cols] = dataframe[str_cols].replace(
            {r'[\x00-\x08\x0b\x0c\x0e-\x1f]': ''}, regex=True
        )

    if os.path.isfile(excel_file):  # if the Excel file already exists
        # Append to existing Excel file
        with pd.ExcelWriter(excel_file, engine='openpyxl', mode='a') as writer:
            dataframe.to_excel(writer, sheet_name=worksheet_name,  index=False)
    else:
        # Create a new Excel file
        with pd.ExcelWriter(excel_file, engine='openpyxl', mode='w') as writer:
            dataframe.to_excel(writer, sheet_name=worksheet_name, index=False)