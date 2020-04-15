# -*- coding: utf-8 -*-
import scrapy
from scrapy.selector import Selector
from selenium import webdriver
from selenium.webdriver.common.by import By
from ..items import SpiderItem
import re
from scrapy import cmdline


class ExampleSpider(scrapy.Spider):
    name = 'task'
    allowed_domains = ['http://www.tauntondeeds.com/Searches/ImageSearch.aspx']
    start_urls = ['http://www.tauntondeeds.com/Searches/ImageSearch.aspx']

    def parse(self, response):

        driver = webdriver.Firefox(executable_path="./geckodriver.exe")
        driver.get("http://www.tauntondeeds.com/Searches/ImageSearch.aspx")

        input_start = driver.find_element_by_id("ctl00_cphMainContent_txtRLStartDate_dateInput_text")
        input_end = driver.find_element_by_id("ctl00_cphMainContent_txtRLEndDate_dateInput_text")
        select = driver.find_element_by_id("ctl00_cphMainContent_ddlRLDocumentType_vddlDropDown")
        btn_search = driver.find_element_by_id("ctl00_cphMainContent_btnSearchRL")

        input_start.send_keys("1/1/2020")
        input_end.send_keys("12/31/2020")

        for option in select.find_elements_by_tag_name('option'):
            if option.text == 'DEED':
                option.click()
                break
        btn_search.click()



        for i in range(77):
            html = driver.page_source
            resp = Selector(text=html)
            table = resp.xpath("//table[@id = 'ctl00_cphMainContent_gvSearchResults']//tbody//tr[@onmouseout='this.className=this.originalClass;']")
            for tabl in table:
                items = SpiderItem()
                items['date'] = tabl.xpath('td[2]//text()').extract()
                items['type'] = tabl.xpath('td[3]//text()').extract()
                items['book'] = tabl.xpath('td[4]//text()').extract()
                items['page_num'] = tabl.xpath('td[5]//text()').extract()
                items['doc_num'] = tabl.xpath('td[6]//text()').extract()
                items['city'] = tabl.xpath('td[7]//text()').extract()
                items['description'] = tabl.xpath('td[8]//text()').extract()
                items['cost'] = None
                items['street_address'] = None
                items['state'] = None
                items['zip'] = None

                cost = re.search("\d{1,}\.\d\d", tabl.xpath('td[8]//text()')[1].extract())
                if cost is not None:
                    items['cost'] = cost.group(0)

                street_address = re.search("\d{1,}\-?\d{1,} ([a-zA-Z]{1,}) ([a-zA-Z]{1,4})", tabl.xpath('td[8]//text()')[1].extract())
                if street_address is not None:
                    items['street_address'] = street_address.group(0)

                state = re.search(" AL | AK | AS | AZ | AR | CA | CO | CT | DE | DC | FL | GA | GU | HI | ID | IL | IN | IA | KS | KY | LA | ME | MD | MH | MA | MI | FM | MN | MS | MO | MT | NE | NV | NH | NJ | NM | NY | NC | ND | MP | OH | OK | OR | PW | PA | PR | RI | SC | SD | TN | UT | VT | VA | VI | WA | WV | WI | WY", tabl.xpath('td[8]//text()')[1].extract())
                if state is not None:
                    items['state'] = state.group(0)

                zip_code = re.search("\d{5}", tabl.xpath('td[8]//text()')[1].extract())
                if zip_code is not None:
                    items['zip'] = zip_code.group(0)

                yield items

            td = "11"
            if i > 10:
                td = "13"
            if i % 10 == 9:
                j = "..."
                driver.find_element_by_xpath(
                    "/html/body/form/div[3]/div[2]/div[2]/div/div[2]/div[3]/table/tbody/tr[1]/td/table/tbody/tr/td[" + td + "]/a[text() = '" + j + "']").click()
            else:
                j = str(i+2)
                driver.find_element_by_xpath(
                    "/html/body/form/div[3]/div[2]/div[2]/div/div[2]/div[3]/table/tbody/tr[1]/td/table/tbody/tr/td/a[text() = '" + j + "']").click()

        cmdline.execute("scrapy crawl task -o result.json -t json".split())
# javascript:__doPostBack('ctl00$cphMainContent$gvSearchResults','Page$2')

