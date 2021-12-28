""" Laborum jobs scraping. """

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
    get_now_date_and_time
    )

def scrape(driver):
    driver.get('https://www.laborum.cl/empleos.html')
    driver.maximize_window()
    driver.implicitly_wait(5)

    create_base_data_folder()
    create_specific_data_folder('laborum')
    filename = generate_file_name('laborum')

    resume_page = None

    if os.path.isfile(filename):
        with open(filename, 'r') as csv_file:
            csv_reader = csv.reader(csv_file, delimiter=',')
            # Get the page when program stopped and add 1
            resume_page = int(list(csv_reader)[-1][-1]) + 1

    total_pages = int(driver.find_element_by_class_name('cDREQp').text)
    if resume_page:
        print(f'Reaching page {resume_page}...')
        current_page = int(driver.find_element_by_class_name('gZtPaa').text)
        while resume_page != current_page:
            next_page = driver.find_element_by_class_name(
                'Pagination__NextPage-sc-el3mid-4')
            next_page.click()  
            current_page = int(driver.find_element_by_class_name('gZtPaa').text)
    else:
        current_page = int(driver.find_element_by_class_name('gZtPaa').text)
    
    while current_page <= total_pages:
        jobs_list = []
        error_counter = 0

        # num_jobs_jobs_per_page = len(driver.find_elements_by_class_name('kaEuLd'))
        jobs_per_page = driver.find_elements_by_class_name('sc-dBaXSw')
        current_page = int(driver.find_element_by_class_name('gZtPaa').text)
        print(f'Page {current_page} of {total_pages}')
        for job in jobs_per_page:
            job.click()
            driver.switch_to.window(driver.window_handles[1])
            try:
                title = driver.find_element_by_xpath(
                    '//*[@id="root"]/div/div[2]/div[2]/div/div[1]/div[1]/div[1]/div/div[1]/div/div/h1').text

                detail = driver.find_element_by_xpath(
                    '//*[@id="root"]/div/div[2]/div[2]/div/div[1]/div[1]/div[1]/div/div[2]/div/div/div/div/div/div/div[2]/div'
                    ).text
            except NoSuchElementException:
                title = driver.find_element_by_xpath(
                    '//*[@id="root"]/div/div[2]/div[1]/div/div[1]/div[1]/div[1]/div/div[1]/div/div/h1').text
                
                detail = driver.find_element_by_xpath(
                    '//*[@id="root"]/div/div[2]/div[1]/div/div[1]/div[1]/div[1]/div/div[2]/div/div/div/div/div/div/div[2]'
                    ).text

            job_data = {
                'title': title,
                'detail': detail,
                'datetime': get_now_date_and_time(),
                'page': current_page,
                }
            jobs_list.append(job_data)
            driver.close()
            driver.switch_to.window(driver.window_handles[0])
                # error_counter = 0
            # except ElementNotInteractableException:
            #     # TODO: What to do here?
            #     print('Job publication has finished')
            #     continue
            #     # import pdb; pdb.set_trace()
            # except NoSuchElementException:
            #     # Job info is not showing, got to next job
            #     continue
            # except StaleElementReferenceException:
            #     import pdb; pdb.set_trace()
            # # TODO: This may not be more necessary
            # except ElementClickInterceptedException as e:
            #     if error_counter > 10:
            #         continue
            #     print(e)
            #     close_extra_tabs(driver)
            #     error_counter += 1

        if jobs_list:
            write_data_to_csv(filename, jobs_list)
        
        if current_page == total_pages:
            # TODO: Find a way to restart it if goes through all pages?
            break

        if current_page < total_pages:
            next_page = driver.find_element_by_class_name(
                'Pagination__NextPage-sc-el3mid-4')
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

    # driver = webdriver.Chrome(
    #     executable_path='base/chromedriver', 
    #     # options=set_chrome_options()
    #     )
    # scrape(driver)