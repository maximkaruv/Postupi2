import os
import csv

class CsvTable:
    def __init__(self, filepath, headers=None):
        self.filepath = filepath
        self.headers = headers

        if not os.path.exists(self.filepath):
            with open(self.filepath, 'w', encoding='utf-8', newline='') as f:
                writer = csv.writer(f)
                if self.headers:
                    writer.writerow(self.headers)

    def add(self, row):
        with open(self.filepath, 'a', encoding='utf-8', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(row)

    def clear(self):
        with open(self.filepath, 'w', encoding='utf-8', newline='') as f:
            writer = csv.writer(f)
            if self.headers:
                writer.writerow(self.headers)
