#class_csv.py
import csv

class CSVFile:
    def __init__(self, file_name):
        self.file_path= file_name

    def read(self):
        with open(self.file_path,'r') as file:
            reader = csv.reader(file)
            data = list(reader)
        return data
    def write(self,data):
        with open(self.file_path,'w',newline='') as file:
            writer = csv.writer(file)
            writer.writerows(data)