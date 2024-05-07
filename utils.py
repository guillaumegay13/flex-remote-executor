import os
import chardet

def create_empty_directory(directory_path):
    if not os.path.exists(directory_path):
        os.makedirs(directory_path)

def detect_encoding(file_path):
    with open(file_path, 'rb') as file:
        raw_data = file.read()
    return chardet.detect(raw_data)['encoding']