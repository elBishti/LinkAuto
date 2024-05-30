from gspread_formatting import *

def column_number_to_letter(column_number):
    string = ""
    while column_number > 0:
        column_number, remainder = divmod(column_number - 1, 26)
        string = chr(65 + remainder) + string
    return string

def format_cells(sheet, df):
    # Apply formatting to the cells
    green_format = CellFormat(backgroundColor=Color(0.5647, 0.9333, 0.5647))
    red_format = CellFormat(backgroundColor=Color(1, 0.4, 0.4))
    bold_format = CellFormat(textFormat=TextFormat(bold=True))

    # Get the letter of the last column
    last_column_letter = column_number_to_letter(len(df.columns))

    # Format the headers
    format_cell_range(sheet, f"A1:{last_column_letter}1", bold_format)

    # Find the index of the "Updated Status" and "Anchor Text" columns
    status_index = df.columns.get_loc("Updated Status")
    anchor_text_index = df.columns.get_loc("Anchor Text")

    # Apply the formatting to the cells
    for i, row in enumerate(df.values, start=2):  # Use df.values to get the rows as lists
        # Format the "Updated Status" column
        if row[status_index] == "Live":
            fmt = green_format
        else:
            fmt = red_format
        format_cell_range(sheet, f"{column_number_to_letter(status_index+1)}{i}", fmt)

        # Format the "Anchor Text" column
        if row[anchor_text_index] != "Not Found":
            fmt = green_format
        else:
            fmt = red_format
        format_cell_range(sheet, f"{column_number_to_letter(anchor_text_index+1)}{i}", fmt)