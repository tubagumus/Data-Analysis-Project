from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd
import time

url = 'https://www.govdata.de/web/guest/daten/-/searchresult/f/type%3Adataset%2Csourceportal%3Abdc08f58-41dc-4f8a-a145-c019805bdeaf%2C/s/relevance_desc'


def get_soup(url):
    options = Options()
    options.add_argument("--start-maximized")
    driver = webdriver.Chrome(options=options)
    driver.get(url)
    time.sleep(20)
    return driver


def get_govdata(driver):
    data = []

    while True:
        soup = BeautifulSoup(driver.page_source, "html.parser")
        page_info = soup.find_all(
            'li', class_='resultentry design-box design-box-padding')

        for i in page_info:
            title_info = i.find('h2').find('a')
            title = title_info.get('title')
            url = title_info.get('href')
            info = i.find('p', class_='h2-teaser').text.strip()

            # 'kategorie'yi kontrol et ve yalnızca bulunursa 'find_next' metodunu kullan
            kategorie_element = i.find(
                'img', alt='Justiz, Rechtssystem und öffentliche Sicherheit')
            kategorie = kategorie_element.find_next(
                'span').text if kategorie_element else None

            year_range = i.find_all('span', id='metadata_temporalCoverageFrom')
            first_date = year_range[0].text if year_range else None
            second_date = year_range[1].text if len(year_range) > 1 else None

            data.append({
                'Url': url,
                'Kategorie': kategorie,
                'Title': title,
                'Info': info,
                'First_date': first_date,
                'Second_date': second_date,
            })

        try:
            body = driver.find_element(By.TAG_NAME, 'body')
            body.send_keys(Keys.PAGE_DOWN)

            # 'Daha Fazla' butonuna tıklandıktan sonra sayfanın yüklenmesini beklemek için WebDriverWait kullan
            more_button = driver.find_element(By.ID, 'searchresults-more-btn')
            more_button.click()

            # Sayfanın sonuna ulaşıldığını kontrol etmek için bekleyin
            WebDriverWait(driver, 10).until(
                EC.visibility_of_element_located(
                    (By.ID, 'searchresults-more-btn'))
            )
        except Exception as e:
            print("Tüm sayfalar işlendi.")
            break

    return data


# Kodu kullanma örneği:
driver = get_soup(url)
show_data = get_govdata(driver)

for entry in show_data:
    print(f'Url : {entry["Url"]}')
    print(f'Title: {entry["Title"]}')
    print(f'Info: {entry["Info"]}')
    print(f'Kategorie : {entry["Kategorie"]}')
    print(f'First_date: {entry["First_date"]}')
    print(f'Second_date: {entry["Second_date"]}')

df = pd.DataFrame(show_data)
print(df)

driver.quit()
