"""
Written By Kai R. Weiner, Lazuli Kleinhans
"""

import csv

def get_CSV_data_as_list(filepath):
    """
    Returns a list of data from a specified CSV file.

    Args:
        filepath : the path leading to the CSV file to be returned as a list
    Return:
        data : the CSV file in list form
    """
    file_to_read = open(filepath)
    read_file = csv.reader(file_to_read)
    data = load_CSV_list(read_file)
    file_to_read.close()
    return data

def load_CSV_list(file):
    """
    Returns a list filled with data from a CSV file

    Args:
        file : the CSV file to be returned as a list
    Return:
        data : the CSV file in list form
    """
    data = []
    for datapoint in file:
        data.append(datapoint)
    return data