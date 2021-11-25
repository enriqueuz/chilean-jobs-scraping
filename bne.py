""" BNE jobs scraping. """

# Selenium
from selenium import webdriver
from selenium.webdriver.common.by import By # Helps get elements through selectors for interaction
from selenium.webdriver.support.ui import WebDriverWait # Helps uses expected conditions and explicit waits
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException

# Setup
from webdriver_manager.chrome import ChromeDriverManager
from base.chrome_options import set_chrome_options

# Others
# import csv
from datetime import datetime
import csv, os, stat
from time import sleep

# driver = webdriver.Chrome(executable_path='/usr/local/bin/chromedriver')
driver = webdriver.Chrome(
    ChromeDriverManager().install(), 
    options=set_chrome_options()
)
driver.get('https://www.bne.cl/')
driver.maximize_window()
driver.implicitly_wait(5)
# driver.set_page_load_timeout(20)

search = driver.find_element_by_id('botonBuscarHome')
search.click()

# Wait for 'Buscando ofertas' modal to dissapear
WebDriverWait(driver, 15).until(
    EC.invisibility_of_element_located(
        (By.CLASS_NAME, 'modal-dialog modal-sm')
        )
    )

driver.switch_to.window # Return focus to window

# Get current page from paginator
current_page = WebDriverWait(driver, 10).until(
    EC.visibility_of_element_located(
        (By.CSS_SELECTOR, '#numerosPagina > li.page-item.active > a')
        )
    )

# Get total number of pages 
current_page = int(current_page.text)
total_pages = driver.find_element_by_xpath('//*[@id="datosPaginacion"]/span[4]')
total_pages = int(total_pages.text)


jobs_list = []

while current_page <= total_pages:
    print(f'Page {current_page} of {total_pages} pages')
    sleep(5)
    num_jobs = len(driver.find_elements_by_class_name('seccionOferta'))
    for i in range(num_jobs):
        print(f'Offer number {i} of {num_jobs} offers in page')

        if i > 0:
            WebDriverWait(driver, 15).until(
                EC.invisibility_of_element_located(
                    (By.CLASS_NAME, 'modal-dialog modal-sm')
                )
            )
        try:
            job=driver.find_element_by_xpath(
                f'/html/body/div[1]/main/div/div[2]/div[1]/div[1]/article[{i + 1}]/div/'\
                    'div[1]/div[1]/div[2]/div/a/span'
                )
        except NoSuchElementException as err:
            continue
        
        job.click()
        job_title = driver.find_element_by_xpath('//*[@id="nombreOferta"]/span').text
        ciuo = driver.find_element_by_xpath('//*[@id="nombreOferta"]/small').text

        contact_information = driver.find_element_by_xpath(
            '/html/body/div/div[2]/div/div/div/section[2]/div[2]/div/article[1]/'\
                'div[2]/div/div/div/div[1]'
                ).text

        description = driver.find_element_by_xpath('/html/body/div/div[2]/div/div/'\
            'div/section[2]/div[2]/div/article[2]/div[2]/div[1]/div/p'
            ).text
        
        details = driver.find_element_by_xpath(
            '/html/body/div/div[2]/div/div/div/section[2]/div[2]/div/article[2]/'\
                'div[2]/div[2]'
                ).text
        
        requirements = driver.find_element_by_xpath(
            '/html/body/div/div[2]/div/div/div/section[2]/div[2]/div/article[3]/div[2]/div'
            ).text
        
        characteristics = driver.find_element_by_xpath('/html/body/div/div[2]/div'\
            '/div/div/section[2]/div[2]/div/article[4]/div[2]'
            ).text
        
        job_data = {
                    'job_title':job_title,
                    'ciuo':ciuo,
                    'contact_information':contact_information,
                    'description':description,
                    'details':details,
                    'requirements':requirements,
                    'characteristics':characteristics
                    }
        
        jobs_list.append(job_data)
        # import pdb; pdb.set_trace()
        driver.back()

        # if current_page < total_pages and i == num_jobs:
        #     next_button = driver.find_element_by_link_text('Siguiente >')
        #     next_button.click()

    if current_page < total_pages:
        # import pdb; pdb.set_trace()
        WebDriverWait(driver, 15).until(
            EC.visibility_of_element_located(
                (By.LINK_TEXT, 'Siguiente >')
                )
            ).click()
        # next_button.click()
        current_page += 1 

filename = 'bne_' + datetime.today().strftime('%Y-%m-%d')

with open(filename, 'w') as csvfile:
    writer = csv.DictWriter(csvfile, fieldnames=job_data.keys())
    writer.writerows(jobs_list)

# Give permission of the file to everyone
os.chmod(filename, stat.S_IRWXU | stat.S_IRWXG | stat.S_IRWXO)

driver.quit()
