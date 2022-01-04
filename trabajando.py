""" Laborum jobs scraping. """

# Selenium
from selenium import webdriver
from selenium.common.exceptions import (
    NoSuchElementException, 
    WebDriverException, 
    ElementNotInteractableException,
    ElementClickInterceptedException,
    StaleElementReferenceException,
    TimeoutException
    )
from selenium.webdriver.common.by import By # Helps get elements through selectors for interaction
from selenium.webdriver.support.ui import WebDriverWait # Helps uses expected conditions and explicit waits
from selenium.webdriver.support import expected_conditions as EC

# Others
from base.chrome_options import set_chrome_options
import csv, os
from time import sleep

# Utils
from base.utils import (
    create_base_data_folder, 
    create_specific_data_folder,
    generate_file_name,
    write_single_data_to_csv, 
    close_extra_tabs,
    get_now_date_and_time
    )

def scrape(driver):
    # driver = webdriver.Chrome(
    #     executable_path='base/chromedriver', 
    #     options=set_chrome_options()
    #     )
    driver.get('https://www.trabajando.cl/trabajo-empleo/chile')
    driver.maximize_window()
    driver.implicitly_wait(5)

    create_base_data_folder()
    create_specific_data_folder('trabajando')
    filename = generate_file_name('trabajando')

    resume_page = None
    jobs_scrapped = 0

    # Continue
    if os.path.isfile(filename):
        with open(filename, 'r') as csv_file:
            csv_reader = csv.reader(csv_file, delimiter=',')
            # Get the page when program stopped and add 1
            jobs_list = list(csv_reader)
            jobs_scrapped = len(jobs_list)
            resume_page = int(jobs_list[-1][-1]) + 1

    if resume_page:
        print(f'Scrolling to page {resume_page}...')
        current_page = 1
        while resume_page != current_page:
            height = driver.execute_script(
                "return document.querySelector('.resultsBox').scrollHeight")
            driver.execute_script(
                f"document.querySelector('.resultsBox').scrollTop={height}")
            WebDriverWait(driver, 10).until(EC.url_changes(driver.current_url))
            current_page = int(driver.current_url.split('page=')[-1])

    total_num_jobs = driver.find_element_by_class_name(
        'resultado_busquedas_listado_oferta_resultado').text
    total_num_jobs = int(total_num_jobs.split(' ')[0])

    i = 1
    while True:
        
        if jobs_scrapped >= total_num_jobs:
            break
        
        print(f'Scraping job {jobs_scrapped + 1} of {total_num_jobs}')
        try:
            job_xpath = f'/html/body/div[7]/div/div/div/div[2]/div[1]/div/div[2]/div[{i}]'
            job = driver.find_element_by_xpath(job_xpath)
            job_text = job.text.split('\n')[0]
            driver.execute_script("arguments[0].click();", job)

            # Wait for the job to load
            WebDriverWait(driver, 20).until(
                EC.text_to_be_present_in_element(
                    (By.ID, "return-to-top"), job_text)
                )

            title = driver.find_element_by_id("return-to-top").text
            if title != job_text:
                # If for any reason the current title does not match the current
                # job, skip it and go to the next one
                i += 1
                continue

            description = driver.find_element_by_xpath(
                '//*[@id="detalle_oferta"]/div[3]/div[1]/div').text

            detail = driver.find_element_by_xpath(
                '//*[@id="detalle_oferta"]/div[3]/div[3]').text

            requirements = driver.find_element_by_xpath(
                '//*[@id="detalle_oferta"]/div[3]/div[5]').text

            page = driver.current_url.split('page=')[-1]

            # On the first page the the url does not include the page yet
            try:
                page = int(page)
            except ValueError:
                page = 1

            job_data = {
                    'title': title, 
                    'description': description, 
                    'detail': detail,
                    'requirements': requirements,
                    'datetime': get_now_date_and_time(),
                    'page': page
                    }

        except ElementNotInteractableException:
            print('Scrolling...')
            driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", job)
        except StaleElementReferenceException:
            close_extra_tabs(driver)
        except ElementClickInterceptedException:
            # TODO: May not be necessary
            print('waiting for element...')
            import pdb; pdb.set_trace()
        except NoSuchElementException:
            # When there are not not more jobs in this page, scroll to 
            # the next one 
            print('Scrolling to next page...')
            height = driver.execute_script(
                "return document.querySelector('.resultsBox').scrollHeight")
            driver.execute_script(
                f"document.querySelector('.resultsBox').scrollTop={height}")
        except TimeoutException as err:
            # If job does not load, go to the next one
            i += i
            continue
        else:
            # If everything goes write, write the data
            write_single_data_to_csv(filename, job_data)
            i += 1
            jobs_scrapped += 1

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
    # driver = webdriver.Chrome(
    #                 executable_path='base/chromedriver', 
    #                 # options=set_chrome_options()
    #                 )
    # scrape(driver)