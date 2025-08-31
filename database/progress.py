import os
import json

class Progress:
    def __init__(self, filepath, headers=None):
        self.filepath = filepath
        self.headers = headers

        if not os.path.exists(self.filepath):
            open(self.filepath, 'w')
    
    pass
