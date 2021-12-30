""" Utils. """

import os, csv
from datetime import datetime

def get_now_date_and_time():
    """ Return now date and time. """
    now = datetime.now().strftime('%d-%m-%Y %H:%M')
    return now

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

def generate_file_name(name):
    """ Generate filename based on the introduced name and today's date. """
    filename = f'data/{name}/{name}_{datetime.today().strftime("%Y-%m-%d")}.csv'
    return filename

def write_data_to_csv(filename, jobs_list):
    """ Check if file exists, create it if it does not and then write 
    scraped data to csv. """
    if not os.path.isfile(filename):
        with open(filename, 'w') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=jobs_list[0].keys())
            writer.writeheader()
    
    with open(filename, 'a') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=jobs_list[0].keys())
        writer.writerows(jobs_list)

def write_single_data_to_csv(filename, job):
    """ Check if file exists, create it if it does not and then write 
    scraped data to csv. """
    if not os.path.isfile(filename):
        with open(filename, 'w') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=job.keys())
            writer.writeheader()
    
    with open(filename, 'a') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=job.keys())
        writer.writerow(job)

def close_extra_tabs(driver):
    """ Close all extra tabs that are opened automatically. """
    num_tabs = len(driver.window_handles)
    # If there is more than one tab close them, this may be a function
    if num_tabs > 1:
        for i in range(num_tabs - 1, 0, -1):
            driver.switch_to.window(driver.window_handles[i])
            driver.close()
            print('Closed Tab No. ', i)
        driver.switch_to.window(driver.window_handles[0])
    else:
        print('No tabs closed')

def get_registries_list_csv(filename):
    """ Return list of jobs in csv. """
    with open(filename, 'r') as csv_file:
                csv_reader = csv.reader(csv_file, delimiter=',')
                jobs_list = list(csv_reader)
                jobs_scrapped = len(jobs_list) - 1
                return jobs_scrapped