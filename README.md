# StockX Web Cralwer

Welcome to the custom StockX web crawler!  This scraper is designed to:

1. Collect data from the #sneaker# section of StockX, scraping information including sneaker name, retail price (converted to usd), average resell, last resell, calculated average profit and the url to the shoe image
2. Automatically create and/or save all scraped data into a .csv file
3. Access the image url to download the shoe image into a local folder
4. The saved image's name will also be written to the .csv corresponding to the shoe, allowing for building convenient dataloaders for deep learning projects
5. Scalable to scrape other sections of Stockx as well, including clothing, merchandise etc. (However these features are not implemented)
