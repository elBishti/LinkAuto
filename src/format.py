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
    yellow_format = CellFormat(backgroundColor=Color(1, 1, 0.4))
    bold_format = CellFormat(textFormat=TextFormat(bold=True))

    # Get the letter of the last column
    last_column_letter = column_number_to_letter(len(df.columns))

    # Format the headers
    format_cell_range(sheet, f"A1:{last_column_letter}1", bold_format)

    # Find the index of the "Updated Status" and "Anchor Text" columns
    status_index = df.columns.get_loc("Updated Status")
    anchor_text_index = df.columns.get_loc("Anchor Text")
    ankar_text_index = df.columns.get_loc("Ankartext")
    to_url_index = df.columns.get_loc("To URL")
    correct_to_url_index = df.columns.get_loc("Correct Link")

    # Apply the formatting to the cells
    for i, row in enumerate(df.values, start=2):
        # Format the "Updated Status" column
        status_code = int(row[status_index])
        if 200 <= status_code < 300:
            fmt = green_format
        else:
            fmt = red_format
        format_cell_range(sheet, f"{column_number_to_letter(status_index+1)}{i}", fmt)

        # Format the "Anchor Text" column
        anchor_text = row[anchor_text_index].strip()
        ankar_text = row[ankar_text_index].strip()
        
        anchor_text_words = set(anchor_text.lower().split())
        ankar_text_words = set(ankar_text.lower().split())

        if anchor_text.lower() == ankar_text.lower():
            fmt = green_format
        elif ankar_text_words.issubset(anchor_text_words):
            fmt = yellow_format
        else:
            fmt = red_format
        format_cell_range(sheet, f"{column_number_to_letter(anchor_text_index+1)}{i}", fmt)

        # Format the "To URL" column
        correct_to_url = row[correct_to_url_index].strip() if row[correct_to_url_index] is not None else ""
        if correct_to_url == "Correct":
            fmt = green_format
        elif correct_to_url.startswith("http"):
            fmt = yellow_format
        else:
            fmt = red_format
        format_cell_range(sheet, f"{column_number_to_letter(correct_to_url_index+1)}{i}", fmt)