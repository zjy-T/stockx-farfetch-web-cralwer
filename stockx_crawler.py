'''The stockx shoe crawler loads into page 1 of stockx/sneakers, goes into every shoe link, and extracts the shoe name,
retail price, average sale price, and the url to its picture. The crawler will continue until a specified number of
pages have been scraped'''

import requests
from bs4 import BeautifulSoup
from tqdm.auto import tqdm
import csv
import re

def stockx_shoe_crawler(max_pages):

    # define the global variables which are called in get_item
    global csv_writer

    # create and opens a .csv file in write mode and loads in the appropriate headlings
    csv_file = open('stockx_sneaker_data.csv', 'w')
    csv_writer = csv.writer(csv_file)
    csv_writer.writerow(['shoe_name', 'retail_price_usd', 'last_sale_usd', 'avg_sale_usd', 'avg_profit', 'image_name', 'image_link', 'source'])

    # define the start page
    page = 1
    count = 1

    # loop through each item of each page to scrape data until until max page
    while page <= max_pages:

        #load starting url with header to bypass security
        url = 'https://stockx.com/sneakers?page=' + str(page)
        headers = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.14; rv:66.0) Gecko/20100101 Firefox/66.0",
                   "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                   "Accept-Language": "en-US,en;q=0.5", "Accept-Encoding": "gzip, deflate", "DNT": "1",
                   "Connection": "close", "Upgrade-Insecure-Requests": "1"}

        # request the url text and create BeautifulSoup object to parse html
        source_code = requests.get(url, headers=headers)
        plain_text = source_code.text
        soup = BeautifulSoup(plain_text, "lxml")

        # parses through each shoe on the page to scrape the data
        for link in tqdm(soup.findAll('div', {'class': 'tile browse-tile false'})):

            # pulls the shoe url
            shoe = link.a
            href = 'https://stockx.com' + shoe.get('href')

            # calls get_item to perform the actual data scraping for the shoe
            get_item(href, count)
            count += 1

        print('{}/{} page(s) have been crawled!'.format(page, max_pages))

        page += 1

    #close the .csv file once all shoes have been scraped
    csv_file.close()
    print('All {} page(s) have been scraped!'.format(max_pages))

def get_item(item_url, count):

    #define the usd - cad exchange rate as prices in html are listed in cad
    cad_usd_ex = 0.76

    #same procedure as before, request shoe url and create a BeuatifulSoup object
    headers = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.14; rv:66.0) Gecko/20100101 Firefox/66.0",
               "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
               "Accept-Language": "en-US,en;q=0.5", "Accept-Encoding": "gzip, deflate", "DNT": "1",
               "Connection": "close", "Upgrade-Insecure-Requests": "1"}
    source_code = requests.get(item_url, headers=headers)
    plain_text = source_code.text
    soup = BeautifulSoup(plain_text, "lxml")

    #scrapes the shoe name, retail price, average sale price, and shoe image url from each shoe link

    source = 'stockx'

    try:
        name = soup.find('div', {'class': 'col-md-12'}).h1.text.strip()
        #print(name)
    except:
        name = None

    try:
        retail = int(soup.find('span', {'data-testid': 'product-detail-retail price'}).text.strip()[1:].replace(',', ''))
        #print('Retail: $' + retail)
    except:
        retail = None
        print('No retail price was recorded for {}'.format(name))

    try:
        last_sale = soup.find('div', {'class': 'sale-value'}).text.strip()[3:].replace(',', '')
        last_sale_usd = int(int(last_sale) * cad_usd_ex)
        #print(last_sale)
    except:
        last_sale_usd = None
        print('No sales have been recorded for {}'.format(name))
        print()

    try:
        avg_sale = int(soup.find('div', {'class': 'gauges'}).select('div > div')[-1].text.strip()[1:].replace(',', ''))
        avg_sale_usd = int(int(avg_sale) * cad_usd_ex)
        avg_profit = int(avg_sale_usd) - int(retail)
    except:
        avg_sale_usd = None
        avg_profit = None
        print('Average sale price cannot be calculated for {}'.format(name))
        print()

    try:
        img_link = soup.find('img', {'data-testid': 'product-detail-image'}).get('src')
        if re.search('.*New-Product-Placeholder.*', img_link) != None:
            img_link = None
    except:
        img_link = None
        print('No image link was provided for {}'.format(name))
        print()

    try:
        image_name = imagedownload(img_link, count, source)
    except:
        image_name = None
        print('Image for {} could not be downloaded'.format(name))
        print()

    #save the data into our .csv file
    try:
        csv_writer.writerow([name, retail, last_sale_usd, avg_sale_usd, avg_profit, image_name, img_link, source])
    except:
        pass
