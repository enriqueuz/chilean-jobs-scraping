""" Utils. """

import os

def create_base_data_folder():
    """ Tries to create data folder, else prints that it already exists. """
    print('Creating data folder')
    try:
        os.mkdir('data')
    except FileExistsError as err:
        print("Folder Exists")

def create_specific_data_folder(folder_name):
    """ Tries to create data folder with a specific name, 
    else prints that it already exists. """
    print('Creating data folder')
    try:
        os.mkdir(f'data/{folder_name}')
    except FileExistsError as err:
        print(f"{folder_name} folder exists")