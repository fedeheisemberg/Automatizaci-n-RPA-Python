#google_sheets.py
import gspread
import pandas as pd

class GoogleSheet:
    def __init__(self, file_name, document, sheet_name):
        self.gc = gspread.service_account(filename=file_name)
        self.sh = self.gc.open(document)
        self.sheet = self.sh.worksheet(sheet_name)
    
    def read_data(self, range): #range = "A1:E1". Data devolvera un array de la fila 1 desde la columna A hasta la E
        data = self.sheet.get(range)
        return data
    
    def read_data_by_uid(self, uid):
        data = self.sheet.get_all_records()
        df = pd.DataFrame(data)
        print(df)
        filtered_data = df[df['id-usuario'] == uid]
        return filtered_data #devuelve un data frame de una tabla, de dos filas siendo la primera las cabeceras de las columnas
    
    def write_data(self, range, values): #range ej "A1:V1", values must be a list of list
        self.sheet.update(range, values)
    
    def write_data_by_uid(self, uid, values):
        # Find the row index based on the UID
        cell = self.sheet.find(uid)
        row_index = cell.row
        # Update the row with the specified values
        self.sheet.update(f"A{row_index}:F{row_index}", values)
    
    def get_last_row_range(self):
        last_row = len(self.sheet.get_all_values()) + 1
        data = self.sheet.get_values()
        range_start = f"A{last_row}"
        range_end = f"{chr(ord('A') + len(data[0]) - 1)}{last_row}"
        return f"{range_start}:{range_end}"
    
    def get_all_values(self):
        #self.sheet.get_all_values() # this return a list of list, so the get_all_records is easier to get values filtering
        return self.sheet.get_all_records() # this return a list of dictionaries so the key is the name column and the value is the value
    
    def get_members(self):
        table_members = self.get_all_values()
        df = pd.DataFrame(table_members)
        members = df['name'].tolist()
        return members # return a list of all emails in the google sheet