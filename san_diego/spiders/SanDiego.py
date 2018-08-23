import scrapy
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from Server.DB import DB
import datetime


class Scraper(scrapy.Spider):
    name = "SanDiego"
    driver = webdriver.Chrome('./chromedriver')
    db = DB()

    def start_requests(self):
        yield scrapy.Request('https://arcc-acclaim.sdcounty.ca.gov/search/SearchTypeRecordDate', callback=self.parse)

    def parse(self, response):
        self.driver.get(response.url)
        self.driver.find_element_by_id("btnButton").click()
        self.driver.find_element_by_id("btnSearch").click()
        WebDriverWait(self.driver, 60).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "#RsltsGrid .t-grid-content table tbody tr .rowNumClass"))
        )
        self.parse_data()

    def parse_data(self):
        try:
            WebDriverWait(self.driver, 10).until(
                EC.visibility_of_element_located(
                    (By.CSS_SELECTOR, '#RsltsGrid .t-grid-content table tbody tr .rowNumClass')))
        except TimeoutException:
            print('No data for selected date.')
            return self.change_date()

        while not self.has_class(self.driver.find_elements_by_css_selector('.t-pager > .t-link')[2], 't-state-disabled'):
            elems = self.driver.find_elements_by_css_selector('.t-grid-content tbody tr')
            for elem in elems:
                row = dict()
                row['apn'] = elem.find_element_by_css_selector('td:nth-child(9)').text.strip()
                id = elem.find_element_by_css_selector('td:nth-child(2)').text
                elem.click()
                WebDriverWait(self.driver, 60).until(lambda d: len(d.window_handles) == 2)
                self.driver.switch_to.window(self.driver.window_handles[1])
                WebDriverWait(self.driver, 60).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, ".detailsTop"))
                )
                row['record_date'] = datetime.datetime.strptime(
                    self.driver.find_elements_by_css_selector('.formInput')[0].text.strip(), '%m/%d/%Y')
                row['doc_number'] = self.driver.find_elements_by_css_selector('.formInput')[3].text.strip()
                row['doc_type'] = self.driver.find_elements_by_css_selector('.listDocDetails')[1].text.strip()
                row['role'] = ''
                row['grantor'] = self.driver.find_elements_by_css_selector('.listDocDetails')[2].text.strip()
                if self.driver.find_elements_by_css_selector('.detailLabel')[10].text.strip() == 'Grantee:':
                    row['grantee'] = self.driver.find_elements_by_css_selector('.listDocDetails')[3].text.strip()
                else:
                    row['grantee'] = ''
                row['county'] = 'San Diego'
                row['state'] = 'CA'
                self.db.insertData(row)
                self.driver.close()
                self.driver.switch_to.window(self.driver.window_handles[0])
            self.driver.find_elements_by_css_selector('.t-pager > .t-link')[2].click()
            WebDriverWait(self.driver, 60).until(EC.visibility_of_element_located((By.CSS_SELECTOR, '.t-refresh.t-loading')))
            WebDriverWait(self.driver, 60).until(
                EC.invisibility_of_element_located((By.CSS_SELECTOR, '.t-refresh.t-loading')))
        self.change_date()

    def change_date(self):
        self.driver.find_element_by_css_selector('.t-icon.t-icon-calendar').click()
        WebDriverWait(self.driver, 60).until(
            EC.visibility_of_element_located((By.CSS_SELECTOR, '.t-state-selected.t-state-focus')))
        try:
            self.driver.find_element_by_css_selector('.t-state-selected.t-state-focus + td .t-link').click()
            self.driver.find_element_by_id("btnSearch").click()
            WebDriverWait(self.driver, 60).until(
                EC.invisibility_of_element_located(
                    (By.CSS_SELECTOR, '#RsltsGrid .t-grid-content table tbody tr .rowNumClass')))
            self.parse_data()
        except NoSuchElementException:
            print('No more dates are available.')
            return False

    def has_class(self, element, css_class):
        if css_class in element.get_attribute("class"):
            return True
        else:
            return False
