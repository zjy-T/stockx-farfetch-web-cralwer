'''The stockx shoe crawler loads into page 1 of stockx/sneakers, goes into every shoe link, and extracts the shoe name,
retail price, average sale price, and the url to its picture. The crawler will continue until a specified number of
pages have been scraped'''

import requests
from bs4 import BeautifulSoup
from tqdm.auto import tqdm
import csv


def far_shoe_crawler(max_pages):

    # define the global variables which are called in get_item
    global csv_writer

    # create and opens a .csv file in write mode and loads in the appropriate headlings
    csv_file = open('farfect_sneaker_data.csv', 'w')
    csv_writer = csv.writer(csv_file)
    csv_writer.writerow(['shoe_name', 'retail_price_usd', 'last_sale_usd', 'avg_sale_usd', 'avg_profit', 'image_name', 'image_link', 'source'])

    # define the start page
    page = 1
    count = 1

    # loop through each item of each page to scrape data until until max page
    while page <= max_pages:

        #load starting url with header to bypass security
        url = 'https://www.farfetch.com/ca/shopping/men/shoes-2/items.aspx?page=' + str(page) + '&view=180&scale=284'

        headers = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.14; rv:66.0) Gecko/20100101 Firefox/66.0",
                   "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                   "Accept-Language": "en-US,en;q=0.5", "Accept-Encoding": "gzip, deflate", "DNT": "1",
                   "Connection": "close", "Upgrade-Insecure-Requests": "1"}

        source_code = requests.get(url, headers=headers)
        plain_text = source_code.text
        soup = BeautifulSoup(plain_text, "lxml")

        print('crawling page {}/{} ...'.format(page, max_pages))
        for link in tqdm(soup.findAll('li', {'class': '_0a5d39 _d85b45'})):
            shoe = link.a
            href = 'https://farfetch.com' + shoe.get('href')

            # calls get_item to perform the actual data scraping for the shoe
            get_item(href, count)
            count += 1

        page += 1

    #close the .csv file once all shoes have been scraped
    csv_file.close()
    print('All {} page(s) have been scraped!'.format(max_pages))

def get_item(item_url, count):

    source = 'farfetch'

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

    try:
        brand = soup.find('span', {'class': '_710567 _346238 _e4b5ec'}).text.strip()
        name = soup.find('span', {'class': '_d85b45 _3c73f1 _d85b45'}).text.strip()
        name = brand + ' - ' + name
    except:
        name = None

    try:
        retail = soup.find('span', {'class': '_3db8ab _0f635f'}).text[1:].strip().replace(',', '')
        retail = int(int(retail) * cad_usd_ex)
    except:
        retail = None
        print('No retail price was recorded for {}'.format(name))
        print()

    try:
        img_link = soup.find('div', {'class': '_d47db0'}).select('div')[1].div.img.get('src')[:-6] + '480.jpg'
    except:
        img_link = None
        print('No image link was provided for {}'.format(name))
        print()

    try:
        image_name = imagedownload(img_link, count, source)
    except:
        image_name = None
        print('Image for {} could not be downloaded, no image link was found'.format(name))

    last_sale_usd = None
    avg_sale_usd = None
    avg_profit = None

    #save the data into our .csv file
    try:
        csv_writer.writerow([name, retail, last_sale_usd, avg_sale_usd, avg_profit, image_name, img_link, source])
    except:
        pass

def imagedownload(url, count, platform):

    img_name = platform + '_' + 'shoe' + str(count) + '.jpg'
    img_path = platform + '_' + 'shoe' + str(count)
    full_path = '/path/to/your/project/' + platform + '_images/' + img_path + '.jpg'
    urllib.request.urlretrieve(url, full_path)
    return img_name
