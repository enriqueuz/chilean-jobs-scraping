""" Chile trabajos jobs scraping. """

# Selenium
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException, WebDriverException
from selenium.webdriver.support.ui import Select

# Others
# from chrome_options import set_chrome_options
from base.chrome_options import set_chrome_options
import csv, os
from time import sleep
from datetime import datetime

# Utils
from base.utils import (
    create_base_data_folder, 
    create_specific_data_folder,
    generate_file_name,
    write_data_to_csv, 
    close_extra_tabs,
    get_now_date_and_time,
    check_new_day
    )


def scrape(driver):
    driver.get('https://www.chiletrabajos.cl/')
    driver.maximize_window()
    driver.implicitly_wait(5)

    create_base_data_folder()
    create_specific_data_folder('chiletrabajos')
    filename = generate_file_name('chiletrabajos')

    search = driver.find_element_by_id('frm-landingPage1-submit')
    search.click()

    # Make search full time jobs first
    job_type = Select(driver.find_element_by_id('tipo'))
    job_type.select_by_visible_text('Full-time')
    search = driver.find_element_by_xpath('//*[@id="buscadorForm"]/div[3]/button')
    search.click()

    resume_page = None
    # TODO Make this a function?
    if os.path.isfile(filename):
        with open(filename, 'r') as csv_file:
            csv_reader = csv.reader(csv_file, delimiter=',')
            # Get the page when program stopped and add 1
            resume_page = int(list(csv_reader)[-1][-1]) + 1

    current_page = int(driver.find_element_by_css_selector(
                "#buscador > div:nth-child(4) > nav > ul > li.page-item.active"
                ).text)

    if resume_page:
        print('Reaching last page scrapped...')
        while resume_page != current_page:
            next_page = driver.find_element_by_link_text('>')
            driver.execute_script("arguments[0].click();", next_page)
            current_page = int(driver.find_element_by_css_selector(
                "#buscador > div:nth-child(4) > nav > ul > li.page-item.active"
                ).text)
    
    start_date = datetime.now().date() 
    import pdb; pdb.set_trace()

    while True:

        current_date = datetime.now().date()

        if current_date > start_date:
            raise Exception('The script started yesterday, restarting...')

        jobs_list = []

        num_jobs_jobs_per_page = len(driver.find_elements_by_class_name('job-item'))
        page = driver.find_element_by_css_selector(
            "#buscador > div:nth-child(4) > nav > ul > li.page-item.active"
            ).text
        print(f'Page number {page}')

        # check_new_day(filename)

        for i in range(num_jobs_jobs_per_page):
            try:
                driver.find_element_by_id('onesignal-slidedown-cancel-button').click()
            except NoSuchElementException:
                pass
            
            print(f'Job number {i + 1} of {num_jobs_jobs_per_page} in page {page}')
            job = driver.find_element_by_xpath(f'//*[@id="buscador"]/div[5]/div[{i + 1}]')
            driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", job)

            try:
                see_more = job.find_element_by_link_text('Ver más')
                see_more.click()
            except Exception as e:
                print('Empty offer, continuing with nex job... ')
                print(e)
                continue

            close_extra_tabs(driver)

            try:
                title = driver.find_element_by_xpath(
                    '/html/body/main/div/div[3]/div[2]/div[1]/h1'
                    ).text
            except WebDriverException:
                # TODO: What to do here?
                continue
                # import pdb; pdb.set_trace()

            general_info = driver.find_element_by_tag_name('tbody').text
            category = [
                line for 
                line in 
                general_info.split('\n') if "Categoría" in line
                ][0]
            category = category.split('Categoría')[-1].strip()

            try:
                detail = driver.find_element_by_xpath(
                    '/html/body/main/div/div[3]/div[2]/div[3]/div[4]/div[3]/p'
                    ).text
            except NoSuchElementException:
                detail = driver.find_element_by_xpath(
                    '/html/body/main/div/div[3]/div[2]/div[3]/div[3]/div[3]/p'
                    ).text

            job_data = {
                'title': title, 
                'general_info': general_info, 
                'detail': detail,
                'category': category,
                'datetime': get_now_date_and_time(),
                'page': page
                }

            jobs_list.append(job_data)
            driver.back()
        
        # Write data to csv
        write_data_to_csv(filename, jobs_list)
        
        # Go to next page
        try:
            next_page = driver.find_element_by_link_text('>')
            driver.execute_script("arguments[0].click();", next_page)
        except NoSuchElementException:
            break

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
