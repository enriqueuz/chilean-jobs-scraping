""" BNE jobs scraping. """

# Selenium
from selenium import webdriver
from selenium.webdriver.common.by import By # Helps get elements through selectors for interaction
from selenium.webdriver.support.ui import WebDriverWait # Helps uses expected conditions and explicit waits
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, WebDriverException

# Others
from base.chrome_options import set_chrome_options
from base.utils import (
    create_base_data_folder, 
    create_specific_data_folder, 
    generate_file_name,
    write_data_to_csv,
    get_now_date_and_time
    )
from datetime import datetime
import csv, os, stat
from time import sleep


def scrape(driver):
    # driver = webdriver.Chrome(
    #     executable_path='base/chromedriver', 
    #     options=set_chrome_options()
    #     )
    driver.get('https://www.bne.cl/')
    driver.maximize_window()
    driver.implicitly_wait(5)

    search = driver.find_element_by_id('botonBuscarHome')
    search.click()

    # Wait for 'Buscando ofertas' modal to dissapear
    WebDriverWait(driver, 15).until(
        EC.invisibility_of_element_located(
            (By.CLASS_NAME, 'modal-dialog modal-sm')
            )
        )

    driver.switch_to.window # Return focus to window

    create_base_data_folder()
    create_specific_data_folder('bne')

    # filename = 'data/bne/bne_' + datetime.today().strftime('%Y-%m-%d') + '.csv'
    filename = generate_file_name('bne')

    resume_page = None

    # If file exists get last page scrapped
    if os.path.isfile(filename):
        with open(filename, 'r') as csv_file:
            csv_reader = csv.reader(csv_file, delimiter=',')
            # Get the page when program stopped and add 1
            resume_page = int(list(csv_reader)[-1][-1]) + 1

    # Get total number of pages 
    total_pages = driver.find_element_by_xpath('//*[@id="datosPaginacion"]/span[4]')
    total_pages = int(total_pages.text)

    # Get current page from paginator
    current_page = WebDriverWait(driver, 10).until(
        EC.visibility_of_element_located(
            (By.CSS_SELECTOR, '#numerosPagina > li.page-item.active > a')
            )
        )
    current_page = int(current_page.text)

    if resume_page:
        print('Reaching last page scrapped...')
        while resume_page != current_page:
            sleep(3)
            WebDriverWait(driver, 15).until(
                EC.visibility_of_element_located(
                    (By.LINK_TEXT, 'Siguiente >')
                    )
                ).click()
            current_page = WebDriverWait(driver, 10).until(
                EC.visibility_of_element_located(
                    (By.CSS_SELECTOR, '#numerosPagina > li.page-item.active > a')
                    )
                )
            current_page = int(current_page.text)
        print(f'Resuming with page {current_page}')
    
    start_date = datetime.now().date()

    while current_page <= total_pages:

        current_date = datetime.now().date()

        if current_date > start_date:
            raise Exception('The script started yesterday, restarting...')
        
        jobs_list = []

        print(f'Page {current_page} of {total_pages} pages')

        sleep(5)
        num_jobs = len(driver.find_elements_by_class_name('seccionOferta'))

        for i in range(num_jobs):
            print(f'Offer number {i + 1} of {num_jobs} offers in page {current_page}')

            if i > 0:
                WebDriverWait(driver, 15).until(
                    EC.invisibility_of_element_located(
                        (By.CLASS_NAME, 'modal-dialog modal-sm')
                    )
                )

            try:
                job = driver.find_element_by_xpath(
                        f'/html/body/div[1]/main/div/div[2]/div[1]/div[1]/article[{i + 1}]/div/'\
                        'div[1]/div[1]/div[2]/div/a/span'
                        )
                job.click()
            except NoSuchElementException as err:
                print(f'Offer number {i + 1} could not be downloaded')
                continue

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
                        'characteristics':characteristics,
                        'datetime': get_now_date_and_time(),
                        'page':current_page
                        }
            
            jobs_list.append(job_data)
            driver.back()
        
        write_data_to_csv(filename, jobs_list)
        # if not os.path.isfile(filename):
        #     with open(filename, 'w') as csvfile:
        #         writer = csv.DictWriter(csvfile, fieldnames=job_data.keys())
        
        # with open(filename, 'a') as csvfile:
        #     writer = csv.DictWriter(csvfile, fieldnames=job_data.keys())
        #     writer.writerows(jobs_list)
        
        if current_page == total_pages:
            # TODO: Find a way to restart it if goes through all pages?
            break

        if current_page < total_pages:
            WebDriverWait(driver, 15).until(
                EC.visibility_of_element_located(
                    (By.LINK_TEXT, 'Siguiente >')
                    )
                ).click()
            current_page += 1 

    # TODO: Necessary?
    # Give permissions to file
    os.chmod(filename, stat.S_IRWXU | stat.S_IRWXG | stat.S_IRWXO)

    driver.quit()

if __name__ == '__main__':
    """ Keep executing the script when it fails except if there is an error 
    with Selenium driver. """
    # import smtplib

    # def send_mail(err):
    #     gmail_user = ''
    #     gmail_password = ''

    #     sent_from = gmail_user
    #     to = [gmail_user]
    #     subject = 'Prueba email scrap'
    #     body = err

    #     email_text = """\
    #     From: %s
    #     To: %s
    #     Subject: %s

    #     %s
    #     """ % (sent_from, ", ".join(to), subject, body)

    #     try:
    #         smtp_server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
    #         smtp_server.ehlo()
    #         smtp_server.login(gmail_user, gmail_password)
    #         smtp_server.sendmail(sent_from, to, email_text)
    #         smtp_server.close()
    #         print ("Email sent successfully!")
    #     except Exception as ex:
    #         print ("Something went wrong….", ex)

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
            # send_mail('The script has stopped \n' + str(err))
        except Exception as err:
            driver.quit()
            print('Chrome exited')
            print(err)
            sleep(3)
            # send_mail(err)

