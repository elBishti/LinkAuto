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

    # Create a list to store the requests
    requests = []


    # Format the headers
    format_cell_range(sheet, f"A1:{last_column_letter}1", bold_format)

    # Find the index of the "Updated Status" and "Anchor Text" columns
    status_index = df.columns.get_loc("Updated Status")
    anchor_text_index = df.columns.get_loc("Anchor Text")
    ankar_text_index = df.columns.get_loc("Ankartext")
    to_url_index = df.columns.get_loc("To URL")
    correct_to_url_index = df.columns.get_loc("Correct Link")
    indexed_index = df.columns.get_loc("Indexed")
    rel_attributes_index = df.columns.get_loc("Rel Attributes")

    # Apply the formatting to the cells
    for i, row in enumerate(df.values, start=2):
        # Format the "Updated Status" column
        try:
            status_code = int(row[status_index])
        except ValueError:
            print(f"Cannot convert {row[status_index]} to an integer.")
            continue        
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
        if correct_to_url == "Found":
            fmt = green_format
        elif correct_to_url.startswith("http"):
            fmt = yellow_format
        else:
            fmt = red_format
        format_cell_range(sheet, f"{column_number_to_letter(correct_to_url_index+1)}{i}", fmt)

        # Format the "Indexed" column
        indexed = row[indexed_index]
        if indexed == "Indexed":
            fmt = green_format
        else:
            fmt = red_format
        format_cell_range(sheet, f"{column_number_to_letter(indexed_index+1)}{i}", fmt)
            
        # Format the "Rel Attributes" column
        rel_attributes = row[rel_attributes_index].strip()
        if rel_attributes == "nofollow" or rel_attributes == "Not Found":
            fmt = red_format
        else:
            fmt = green_format
        format_cell_range(sheet, f"{column_number_to_letter(rel_attributes_index+1)}{i}", fmt)


    for column_index in [status_index, anchor_text_index, correct_to_url_index, indexed_index, rel_attributes_index]:
        requests.append({
            "repeatCell": {
                "range": {
                    "sheetId": sheet.id,
                    "startRowIndex": i - 1,
                    "endRowIndex": i,
                    "startColumnIndex": column_index,
                    "endColumnIndex": column_index + 1
                },
                "cell": {
                    "userEnteredFormat": fmt
                },
                "fields": "userEnteredFormat(backgroundColor)"
            }
        })

    # Send the batch update
    sheet.spreadsheet.batch_update({"requests": requests})
