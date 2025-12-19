import os
import glob
import json
import time
import argparse

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def load_scenarios(tsv_path, markdown_dir):
    scenarios = []
    for line in open(tsv_path):
        fields = line.strip().split('\t')
        link = fields[0]
        basename = fields[1]
        title = fields[2]
        scenario_path = f'{markdown_dir}/{basename}.wd'
        scenario_text = open(scenario_path).read()
        img_paths = glob.glob(f'{markdown_dir}/{basename}_*.png')
        scenarios.append((link, title, scenario_text, img_paths))
    return scenarios

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--tsv-path', required=True)
    parser.add_argument('--markdown-dir', required=True)
    args = parser.parse_args()

    # load scenarios to memory
    scenarios = load_scenarios(args.tsv_path, args.markdown_dir)

    # load config
    with open('config.json') as json_file:
        config = json.load(json_file)
    firefox_bin = config['firefox_bin']
    gecko_bin = config['gecko_bin']
    username = config['username']
    password = config['password']

    # set up browser
    options = Options()
    options.binary_location = firefox_bin
    service = Service(executable_path=gecko_bin)
    driver = webdriver.Firefox(options=options, service=service)

    # log in to Wikidot
    wikidot_url = 'http://fairfieldproject.wikidot.com/'
    driver.get(wikidot_url)
    sign_in_btn = driver.find_element(By.CLASS_NAME, 'login-status-sign-in')
    sign_in_btn.click()

    handles = driver.window_handles
    driver.switch_to.window(handles[1])

    element_present = EC.presence_of_element_located((By.NAME, 'login'))
    WebDriverWait(driver, 10).until(element_present)

    username_field = driver.find_element(By.NAME, 'login')
    username_field.send_keys(username)
    password_field = driver.find_element(By.NAME, 'password')
    password_field.send_keys(password)
    sign_in_btn = driver.find_element(By.XPATH, '//button')
    sign_in_btn.click()
    driver.switch_to.window(handles[0])

    for link, title, scenario_text, img_paths in scenarios:
        print(link)
        driver.get(link)
        element_present = EC.presence_of_element_located((By.ID, 'create-it-now-link'))
        WebDriverWait(driver, 10).until(element_present)
        create_link = driver.find_element(By.XPATH, '//ul[@id="create-it-now-link"]/li/a')
        create_link.click()

        element_present = EC.presence_of_element_located((By.ID, 'edit-page-title'))
        WebDriverWait(driver, 10).until(element_present)
        title_field = driver.find_element(By.ID, 'edit-page-title')
        title_field.clear()
        title_field.send_keys(title)
        text_area = driver.find_element(By.ID, 'edit-page-textarea')
        text_area.clear()
        text_area.send_keys(scenario_text)
        save_btn = driver.find_element(By.ID, 'edit-save-button')
        save_btn.click()
        time.sleep(5)

        for img_path in img_paths:
            img_path = os.path.abspath(img_path)
            print(f'uploading image {img_path}')

            driver.refresh()
            element_present = EC.presence_of_element_located((By.ID, 'files-button'))
            WebDriverWait(driver, 10).until(element_present)
            files_link = driver.find_element(By.ID, 'files-button')
            files_link.click()
            element_present = EC.presence_of_element_located((By.ID, 'show-upload-button'))
            WebDriverWait(driver, 10).until(element_present)
            upload_link = driver.find_element(By.ID, 'show-upload-button')
            upload_link.click()
            element_present = EC.presence_of_element_located((By.ID, 'upload-userfile'))
            WebDriverWait(driver, 10).until(element_present)
            file_input = driver.find_element(By.ID, 'upload-userfile')
            file_input.send_keys(img_path)
            upload_btn = driver.find_element(By.XPATH, '//input[@type="button" and @value="Upload"]')
            upload_btn.click()
            time.sleep(1)
            WebDriverWait(driver, 60).until(EC.invisibility_of_element_located((By.ID, 'odialog-container')))
            time.sleep(1)

