""" Computrabajo jobs scraping. """

# Selenium
from selenium import webdriver
from selenium.common.exceptions import (
    NoSuchElementException, 
    WebDriverException, 
    ElementNotInteractableException,
    ElementClickInterceptedException,
    StaleElementReferenceException
    )
# from selenium.webdriver.support.ui import Select

# Others
# from chrome_options import set_chrome_options
from base.chrome_options import set_chrome_options
import csv, os
from time import sleep

# Utils
from base.utils import (
    create_base_data_folder, 
    create_specific_data_folder,
    generate_file_name,
    write_data_to_csv, 
    close_extra_tabs,
    get_now_date_and_time,
    get_registries_list_csv
    )

def scrape(driver):
    driver.get('https://www.computrabajo.cl/empleos-en-rmetropolitana')
    driver.maximize_window()
    driver.implicitly_wait(5)

    create_base_data_folder()
    create_specific_data_folder('computrabajo')
    filename = generate_file_name('computrabajo')
    
    resume_page = None

    # Continue
    if os.path.isfile(filename):
        with open(filename, 'r') as csv_file:
            csv_reader = csv.reader(csv_file, delimiter=',')
            # Get the page when program stopped and add 1
            jobs_list = list(csv_reader)
            jobs_scrapped = len(jobs_list)
            resume_page = int(jobs_list[-1][-1]) + 1

    
    if resume_page:
        current_page = 1
        print('Reaching last page scrapped...')
        while resume_page != current_page:
            next_page = driver.find_element_by_link_text('Siguiente')
            next_page.click()
            current_page = driver.find_element_by_class_name(
                'pag_numeric').find_element_by_class_name('sel')
            current_page = int(current_page.text)
    
        
    total_num_jobs = driver.find_element_by_xpath(
        '/html/body/main/div[2]/div[2]/div[1]/div[1]/div[1]/h1/span').text
    total_num_jobs = int(total_num_jobs.replace('.', ''))
    jobs_scrapped = 0

    while total_num_jobs > jobs_scrapped:
        jobs_list = []
        num_jobs_in_page = len(driver.find_elements_by_tag_name('article'))
        current_page = driver.find_element_by_class_name(
            'pag_numeric').find_element_by_class_name('sel')
        current_page = int(current_page.text)
        print(f'Page {current_page}')

        for i in range(num_jobs_in_page):

            number_of_job = jobs_scrapped + i + 1
            print(f'Scraping job {number_of_job} of {total_num_jobs}')
            job = driver.find_element_by_xpath(
                f'/html/body/main/div[2]/div[2]/div[1]/div[2]/article[{i + 1}]')
            try:
                driver.execute_script("arguments[0].click();", job)
            except ElementClickInterceptedException as e:
                print(e)
                import pdb; pdb.set_trace()

            try:
                title = driver.find_element_by_xpath(
                    '/html/body/main/div[1]/h1').text
            except NoSuchElementException:
                print(f'Jon {number_of_job} is no long available')
                driver.back()
                continue

            description = driver.find_element_by_xpath(
                '/html/body/main/div[2]/div/div[2]/div[2]/p[1]').text
            requirements = driver.find_element_by_xpath(
                '/html/body/main/div[2]/div/div[2]/div[2]/ul').text

            job_data = {
                'title': title,
                'description': description,
                'requirements': requirements,
                'datetime': get_now_date_and_time(),
                'page': current_page
            }
            jobs_list.append(job_data)
            driver.back()
        
        write_data_to_csv(filename, jobs_list)
        jobs_scrapped = get_registries_list_csv(filename)
        
        if jobs_scrapped < total_num_jobs:
            next_page = driver.find_element_by_link_text('Siguiente')
            next_page.click()


if __name__ == '__main__':
    """ Keep executing the script when it fails except if there is an error 
    with Selenium driver. """
    while True:
        try:
            driver = webdriver.Chrome(
                executable_path='base/chromedriver', 
                options=set_chrome_options()
                )
        except Exception as err:
            print(err)
            print(f'Script stopped due to {err}')
            break
         
        try:
            scrape(driver)
        except WebDriverException as err:
            print(err)
            driver.quit()
            print('Chrome exited due to web driver')
        except Exception as err:
            driver.quit()
            print('Chrome exited')
            print(err)
            sleep(3)